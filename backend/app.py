from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:password@localhost/greener-grocer'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = 'secret string'

db = SQLAlchemy(app)

class Farmer(db.Model):
    username = db.Column(db.String, primary_key=True)
    name = db.Column(db.String, nullable=False)
    
    store_name = db.Column(db.String, nullable=False)
    store_id = db.Column(db.Integer, unique=True, nullable=False)
    location = db.Column(db.String, nullable=False)
    type = db.Column(db.String, nullable=False)
    bio = db.Column(db.String, nullable=False)


    def __init__(self, username, name, store_name, store_id, location, type, bio):
        self.username = username
        self.name = name

        self.store_name = store_name
        self.store_id = store_id
        self.location = location
        self.type = type
        self.bio = bio


class Customer(db.Model):
    username = db.Column(db.String, primary_key=True)
    name = db.Column(db.String, nullable=False)

    def __init__(self, username, name):
        self.username = username
        self.name = name

curr_id = 0

@app.route('/')
def home():
    return '<a href="/addfarmer"><button> Are you a farmer? </button></a> Or  <a href="/addcustomer"><button> Are you a customer? </button></a>'


@app.route("/addfarmer")
def addperson():
    return render_template("farmer-signup.html")

@app.route("/farmeradd", methods=['POST'])
def farmeradd():
    global curr_id
    username = request.form["username"]
    name = request.form["name"]
    store_name = request.form["store_name"]
    location = request.form["location"]
    type = request.form["type"]
    bio = request.form["bio"]
    entry = Farmer(username, name, store_name, curr_id, location, type, bio)
    curr_id = curr_id + 1
    db.session.add(entry)
    db.session.commit()

    return render_template("successful.html")

@app.route("/addcustomer")
def addcustomer():
    return render_template("customer-signup.html")


@app.route("/customeradd", methods=['POST'])
def customeradd():
    print("hi")
    username = request.form["username"]
    name = request.form["name"]
    entry = Customer(username, name)
    db.session.add(entry)
    db.session.commit()

    return render_template("successful.html")

if __name__ == '__main__':
    db.create_all()
    app.run()

