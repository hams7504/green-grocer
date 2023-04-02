from flask import Flask, render_template, request, url_for, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from werkzeug.exceptions import abort
from flask_bcrypt import Bcrypt
import datetime

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:<REDACTEDFORPRIVACY>@localhost/greener-grocer'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = 'secret string'

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    user_types = {'farmer': Farmer, 'customer': Customer}
    for user_type, user_class in user_types.items():
        user = user_class.query.get(user_id)
        if user:
            user.user_type = user_type
            return user
    return None

class Farmer(db.Model, UserMixin):
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

    def get_id(self):
        return str(self.username)

curr_id = 0

class RegisterFarmerForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})
    name = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Name"})
    store_name = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Store Name"})
    location = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Location"})
    type = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Types of Produce"})
    bio = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Bio (timings, dietary restrictions)"})
    submit = SubmitField("Register")

    def validate_username(self, username):
        existing_farmer_username = Farmer.query.filter_by(username=username.data).first()
        if existing_farmer_username:
            raise ValidationError("That username already exists. Please choose a different one.")


class LoginFarmerForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})
    submit = SubmitField("login")


class Customer(db.Model, UserMixin):
    username = db.Column(db.String, primary_key=True)

    def __init__(self, username):
        self.username = username

    def get_id(self):
        return str(self.username)
    
curr_post_id = 0
    
class Posts(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False)
    created = db.Column(db.String, nullable=False)
    title = db.Column(db.String, nullable=False)
    content = db.Column(db.String, nullable=False)

    def __init__(self, id, username, created, title, content):
        self.id = id
        self.username = username
        self.created = created
        self.title = title
        self.content = content

    def get_id(self):
        return str(self.id)


class RegisterCustomerForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})
    submit = SubmitField("Register")

    def validate_username(self, username):
        existing_customer_username = Customer.query.filter_by(username=username.data).first()
        if existing_customer_username:
            raise ValidationError("That username already exists. Please choose a different one.")


class LoginCustomerForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})
    submit = SubmitField("login")


@app.route('/')
def home():
    return render_template('homepage.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')

@app.route("/addfarmer", methods=['GET', 'POST'])
def addfarmer():
    global curr_id

    form = RegisterFarmerForm()

    if form.validate_on_submit():
        new_farmer = Farmer(username=form.username.data, name=form.name.data, store_name=form.store_name.data, store_id=curr_id, location=form.location.data, type=form.type.data, bio=form.bio.data)
        curr_id = curr_id + 1
        db.session.add(new_farmer)
        db.session.commit()
        return redirect(url_for('farmerlogin'))

    return render_template('farmer-signup.html', form=form)

@app.route("/farmerlogin", methods=['GET', 'POST'])
def farmerlogin():
    form = LoginFarmerForm()
    if form.validate_on_submit():
        farmer = Farmer.query.filter_by(username=form.username.data).first()
        if farmer:
            login_user(farmer)
            return redirect(url_for('farmerdashboard'))
    return render_template('farmer-login.html', form=form)

@app.route('/farmerdashboard', methods=['GET', 'POST'])
@login_required
def farmerdashboard():
    farmer = Farmer.query.filter_by(username=current_user.username).first()
    return render_template('farmer-dashboard.html', farmer=farmer)

@app.route('/farmerlogout', methods=['GET', 'POST'])
@login_required
def farmerlogout():
    logout_user()
    return redirect(url_for('login'))

@app.route("/addcustomer", methods=['GET', 'POST'])
def addcustomer():
    form = RegisterCustomerForm()

    if form.validate_on_submit():
        new_customer = Customer(username=form.username.data)
        db.session.add(new_customer)
        db.session.commit()
        return redirect(url_for('customerlogin'))

    return render_template('customer-signup.html', form=form)

@app.route("/customerlogin", methods=['GET', 'POST'])
def customerlogin():
    form = LoginCustomerForm()
    if form.validate_on_submit():
        customer = Customer.query.filter_by(username=form.username.data).first()
        if customer:
            login_user(customer)
            return redirect(url_for('customerdashboard'))
    return render_template('customer-login.html', form=form)

@app.route('/customerdashboard', methods=['GET', 'POST'])
@login_required
def customerdashboard():
    farmers = Farmer.query.all()
    return render_template('customer-dashboard.html', farmers=farmers)

@app.route('/customerlogout', methods=['GET', 'POST'])
@login_required
def customerlogout():
    logout_user()
    return redirect(url_for('login'))

def get_post(post_id):
    post = Posts.query.filter_by(id=post_id).first()
    if post is None:
        abort(404)
    return post

@app.route('/<int:post_id>')
@login_required
def post(post_id):
    post = get_post(post_id)
    return render_template('post.html', post=post)

@app.route('/forum', methods=['GET', 'POST'])
@login_required
def forum():
    posts = Posts.query.all()
    return render_template('forum.html', posts=posts)

@app.route('/createpost', methods=['GET', 'POST'])
@login_required
def createpost():
    global curr_post_id
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        if not title:
            flash('Title is required!')
        else:
            new_post = Posts(id=curr_post_id, username=current_user.username, created=datetime.datetime.now(), title=title, content=content)
            curr_post_id = curr_post_id + 1
            db.session.add(new_post)
            db.session.commit()
            return redirect(url_for('forum'))

    return render_template('create-post.html')

@app.route('/<int:id>/edit', methods=('GET', 'POST'))
@login_required
def edit(id):
    """Edit existing posts"""
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        
        if not title:
            flash('Title is required!')
        else:
            db.session.delete(post)
            new_post = Posts(id=id, username=current_user.username, created=datetime.datetime.now(), title=title, content=content)
            db.session.add(new_post)
            db.session.commit()
            return redirect(url_for('forum'))

    return render_template('edit.html', post=post)

@app.route('/<int:id>/delete', methods=('POST', 'GET'))
@login_required
def delete(id):
    post = get_post(id)
    db.session.delete(post)
    db.session.commit()
    flash('"{}" was successfully deleted!'.format(post.title))
    return redirect(url_for('forum'))
    
if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)

