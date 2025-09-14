from flask import Flask, render_template, request, redirect, url_for, session, flash

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os


app = Flask(__name__)


app.secret_key = os.urandom(24)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    statements = db.relationship('Statement', backref='user', lazy=True)

class Statement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    catagory = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


@app.template_filter('currencyFormat')
def currencyFormat(value):
    try:
        value = float(value)
        return f"{value:,.2f}"
    except:
        return "0.00"


@app.route("/")
def home():
    return redirect(url_for("login"))

@app.route("/register", methods=["GET", "POST"])
def register():
    message = ""
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            message = "Email นี้ถูกใช้งานแล้ว!"
        else:
            hashed_password = generate_password_hash(password)
            new_user = User(email=email, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            message = "สมัครสมาชิกสำเร็จ! กำลังไปหน้า Login 😎😎😎"

    return render_template("register.html", message=message)

@app.route("/login", methods=["GET", "POST"])
def login():
    message = ""
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session["user_id"] = user.id
            return redirect("/showData")
        else:
            message = "Email หรือ Password ไม่ถูกต้อง"
    return render_template("login.html", message=message)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/index")
def index():
    if "user_id" not in session:
        return redirect("/login")
    return render_template("index.html")

@app.route("/addStatement", methods=["POST"])
def addStatement():
    user_id = session.get("user_id")
    if not user_id:
        return redirect("/login")

    from datetime import datetime
    date_str = request.form["date"]
    date = datetime.strptime(date_str, "%Y-%m-%d").date()
    
    name = request.form["name"]
    amount = float(request.form["amount"])
    catagory = request.form["catagory"]

    statement = Statement(date=date, name=name, amount=amount, catagory=catagory, user_id=user_id)
    db.session.add(statement)
    db.session.commit()

    return redirect("/index")


@app.route("/showData")
def showData():
    user_id = session.get("user_id")
    if not user_id:
        return redirect("/login")
    statements = Statement.query.filter_by(user_id=user_id).all()
    return render_template("statements.html", statements=statements)

@app.route("/delete/<int:id>")
def deleteStatement(id):
    user_id = session.get("user_id")
    if not user_id:
        return redirect("/login")
    state = Statement.query.filter_by(id=id, user_id=user_id).first()
    if state:
        db.session.delete(state)
        db.session.commit()
    return redirect("/showData")

@app.route("/edit/<int:id>", methods=["GET", "POST"])
def editStatement(id):
    user_id = session.get("user_id")
    if not user_id:
        return redirect("/login")

    state = Statement.query.filter_by(id=id, user_id=user_id).first()
    if not state:
        flash("ไม่พบข้อมูลที่จะแก้ไข")
        return redirect("/")

    if request.method == "POST":

        name = request.form.get("name")
        amount = request.form.get("amount")
        catagory = request.form.get("catagory")
        date = request.form.get("date")

        if not all([name, amount, catagory, date]):
            flash("กรุณากรอกข้อมูลให้ครบ")
            return redirect(f"/edit/{id}")


        state.name = name
        state.amount = amount
        state.catagory = catagory
        state.date = date

        db.session.commit()
        flash("แก้ไขสำเร็จ")
        return redirect("/")


    return render_template("edit.html", state=state)


@app.route("/updateStatement", methods=["POST"])
def updateStatement():
    user_id = session.get("user_id")
    if not user_id:
        return redirect("/login")

    id = request.form.get("id")
    if not id:
        flash("ไม่พบ ID ของรายการ")
        return redirect("/showData")
    id = int(id)

    state = Statement.query.filter_by(id=id, user_id=user_id).first()
    if not state:
        flash("ไม่พบข้อมูลที่จะอัปเดต")
        return redirect("/showData")

    date = request.form.get("date")
    name = request.form.get("name")
    amount = request.form.get("amount")
    catagory = request.form.get("catagory")

    if not all([date, name, amount, catagory]):
        flash("กรุณากรอกข้อมูลให้ครบ")
        return redirect(f"/edit/{id}")

    # แปลงชนิดข้อมูลให้ตรงกับ model
    try:
        state.date = datetime.strptime(date, "%Y-%m-%d").date() 
        state.name = name
        state.amount = float(amount)
        state.catagory = catagory
    except Exception as e:
        flash(f"ข้อมูลไม่ถูกต้อง: {e}")
        return redirect(f"/edit/{id}")

    db.session.commit()
    flash("แก้ไขสำเร็จ")
    return redirect("/showData")




with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)