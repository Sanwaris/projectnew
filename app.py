from flask import Flask , render_template , request, redirect
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Statement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    number = db.Column(db.Integer, nullable=False)
    catagory = db.Column(db.String(50), nullable=False)

@app.template_filter()
def currency(value):
    try:
        value = float(value)
        return "{:,.2f}".format(value)
    except (ValueError, TypeError):
        return "-"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/addStatement" , methods = ['POST'])
def addStatement():
    date = request.form["date"]
    name = request.form["name"]
    number = request.form["number"]
    catagory = request.form["catagory"]
    new_statement = Statement(date=date, name=name, number=number, catagory=catagory)
    db.session.add(new_statement)
    db.session.commit()
    return redirect("/showData")

@app.route("/showData")
def showData() :
    statement = Statement.query.all()  
    return render_template("statements.html" , statement = statement)

@app.route("/delete/<int:id>")
def delete(id) :
    statement = Statement.query.filter_by(id=id).first()
    db.session.delete(statement)
    db.session.commit()
    return redirect("/showData")

@app.route("/edit/<int:id>")
def edit(id):
    statement = Statement.query.filter_by(id=id).first()
    return render_template("edit.html", statement=statement)

@app.route("/editStatement/<int:id>", methods=["POST"])
def editStatement(id):
    statement = Statement.query.get_or_404(id)
    statement.date = request.form["date"]
    statement.name = request.form["name"]
    statement.number = int(request.form["number"])
    statement.catagory = request.form["catagory"]
    db.session.commit()
    return redirect("/showData")

@app.route("/update/<int:id>", methods=["POST"])
def update(id):
    statement = Statement.query.get_or_404(id)
    statement.date = request.form["date"]
    statement.name = request.form["name"]
    statement.number = int(request.form["number"])
    statement.catagory = request.form["catagory"]
    db.session.commit()
    return redirect("/showData")
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug = True)
