import os
from flask import Flask, flash, redirect, render_template, request, url_for
from flask_bootstrap import Bootstrap
from flask_login import (LoginManager, UserMixin, current_user, login_required,login_user, logout_user)
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_wtf import FlaskForm
from werkzeug.security import check_password_hash, generate_password_hash
from wtforms import StringField, SubmitField, BooleanField, RadioField, TextAreaField
from wtforms.validators import URL, DataRequired
from datetime import datetime


application = Flask(__name__)
application.secret_key = os.urandom(24)
Bootstrap(application)


application.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
db = SQLAlchemy(application)


login_manager = LoginManager()
login_manager.init_application(application)


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(user_id)


application.application_context().push()


# your databases
class Cafes(db.Model):
    __tablename__ = "cafes"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=False, nullable=False)
    map_url = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    address = db.Column(db.String(250), nullable=False)
    has_sockets = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.String(250), nullable=False)
    has_wifi = db.Column(db.String(250), nullable=False)
    can_take_calls = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    coffee_price = db.Column(db.Integer, nullable=False)
    cafe_rating = db.Column(db.Integer, nullable=False)
    rating = relationship("Ratings", back_populates="cafe")
    reviews = relationship("Reviews", back_populates="cafe_reviews")

    def __repr__(self):
        return f"Item('{self.name}', {self.location}, {self.address})"
    

class Ratings(db.Model):
    __tablename__ = "ratings"
    id = db.Column(db.Integer, primary_key=True)
    cafe_id = db.Column(db.Integer, db.ForeignKey("cafes.id"))
    cafe = relationship("Cafes", back_populates="rating")
    rating_one = db.Column(db.Integer, nullable=False)
    rating_two = db.Column(db.Integer, nullable=False)
    rating_three = db.Column(db.Integer, nullable=False)
    submissions = db.Column(db.Integer, nullable=False)
    sum_ratings = db.Column(db.Integer, nullable=False)
    rating = db.Column(db.Integer, nullable=False)


class Users(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    reviews = relationship("Reviews", back_populates="author_reviews")

class Reviews(db.Model):
    __tablename__ = "reviews"
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    author_reviews = relationship("Users", back_populates="reviews")
    cafe_id = db.Column(db.Integer, db.ForeignKey("cafes.id"))
    cafe_reviews = relationship("Cafes", back_populates="reviews")
    review = db.Column(db.String(500), nullable=False)


# with application.application_context():
#     db.create_all()


# forms
class NewCafeForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    map_url = StringField('Map URL', validators=[DataRequired(), URL()])
    img_url = StringField('Image URL', validators=[DataRequired(), URL()])
    location = StringField('Cafe Town', validators=[DataRequired()])
    address = StringField('Address', validators=[DataRequired()])
    has_sockets = StringField('Any Sockets', validators=[DataRequired()])
    has_toilet = StringField('Any Toilets', validators=[DataRequired()])
    has_wifi = StringField('Wifi', validators=[DataRequired()])
    can_take_calls = StringField('Are Calls Allowed', validators=[DataRequired()])
    seats = StringField('Seats', validators=[DataRequired()])
    coffee_price = StringField('Coffee Price', validators=[DataRequired()])
    submit = SubmitField('Submit')


class RegisterForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    password = StringField('Password', validators=[DataRequired()])
    submit = SubmitField('Submit')


class LoginForm(FlaskForm):
    email = StringField('Email', render_kw={"placeholder": "Enter Email"}, validators=[DataRequired()])
    password = StringField('Password', render_kw={"placeholder": "Enter Password"}, validators=[DataRequired()])
    submit = SubmitField('Submit')

# filter form for the towns and cafes section
class FilterForm(FlaskForm):
    has_sockets = BooleanField('Has Sockets')
    has_toilet = BooleanField('Has Toilets')
    has_wifi = BooleanField('Wifi')
    can_take_calls = BooleanField('Are Calls Allowed')
    has_seats = BooleanField('Has Seats')
    submit = SubmitField('Filter')

# rating form for the cafe page
class RatingForm(FlaskForm):
    cafe_rating = RadioField('Do you like working from here?', choices=[(0, 'No'), (50, 'Yes'), (100, "Definitely!")], validators=[DataRequired()])
    submit = SubmitField('Submit')

# review form for the cafe page
class ReviewForm(FlaskForm):
    review = TextAreaField(label='', default='', validators=[DataRequired()], render_kw={"placeholder": "'What is it like working from here?"})
    submit = SubmitField('Submit')


@application.route('/')
def home():

    return render_template('index.html', logged_in=current_user.is_authenticated)


@application.route('/towns')
def towns():
    cafes = Cafes.query.all()
    
    towns_with_cafes = {}
    for cafe in cafes:
        town = cafe.location
        if town not in towns_with_cafes:
            towns_with_cafes[town] = set()
        towns_with_cafes[town].add(cafe.name)

    return render_template('all_towns.html', towns_with_cafes=towns_with_cafes, logged_in=current_user.is_authenticated)


@application.route('/database/<name>/<town>', methods=['GET', 'POST'])
def database(name, town):
    form = FilterForm()

    if form.validate_on_submit():
        has_sockets = form.has_sockets.data
        has_toilet = form.has_toilet.data
        has_wifi = form.has_wifi.data
        can_take_calls = form.can_take_calls.data
        has_seats = form.has_seats.data
    else:
        has_sockets = None
        has_toilet = None
        has_wifi = None
        can_take_calls = None
        has_seats = None

    query = Cafes.query.filter_by(name=name, location=town)

    if has_sockets:
        query = query.filter_by(has_sockets="Yes")
    if has_toilet:
        query = query.filter_by(has_toilet="Yes")
    if has_wifi:
        query = query.filter_by(has_wifi="Yes")
    if can_take_calls:
        query = query.filter_by(can_take_calls="Yes")
    if has_seats:
        query = query.filter_by(seats="Yes")

    all_cafes = query.all()

    return render_template('town_cafe.html', cafes=all_cafes, name=name, town=town, form=form)


@application.route('/cafe/<int:cafe_id>', methods=['GET', 'POST'])
def cafe(cafe_id):
    rating_form = RatingForm()
    review_form = ReviewForm()
    new_cafe = NewCafeForm()

    request_review = Reviews.query.filter_by(cafe_id=cafe_id).all()
    
    
    if rating_form.validate_on_submit():
        coffe_shop_rating = rating_form.cafe_rating.data

        if coffe_shop_rating == "100":
            new_rating_three = Ratings(cafe_id=cafe_id,rating_one=0,rating_two=0,rating_three=coffe_shop_rating,submissions=0,sum_ratings=0,rating=0)
            db.session.add(new_rating_three)
            db.session.commit()

        elif coffe_shop_rating == "50":
            new_rating_three = Ratings(cafe_id=cafe_id,rating_one=0,rating_two=coffe_shop_rating,rating_three=0,submissions=0,sum_ratings=0,rating=0)
            db.session.add(new_rating_three)
            db.session.commit()

        elif coffe_shop_rating == "0":
            new_rating_three = Ratings(cafe_id=cafe_id,rating_one=coffe_shop_rating,rating_two=0,rating_three=0,submissions=0,sum_ratings=0,rating=0)
            db.session.add(new_rating_three)
            db.session.commit()
        
    request_rating_from_db = Ratings.query.filter_by(cafe_id=cafe_id).all()
    
    sum_of_all = 0    
    
    for rating in request_rating_from_db:
        sum_of_all += rating.rating_one
        sum_of_all += rating.rating_two
        sum_of_all += rating.rating_three

    try:
        new_rating = sum_of_all/len(request_rating_from_db)
    except ZeroDivisionError:
        print('ZeroDivisionError')
        new_rating = sum_of_all/1

    cafe_to_update = Cafes.query.filter_by(id=cafe_id).first()

    if cafe_to_update:
        # we are not adding but just updating the cafe_rating value of this specific cafe
        cafe_to_update.cafe_rating = new_rating
        db.session.commit()
    else:
        print(f"Cafe with ID {cafe_id} not found.")

    if review_form.validate_on_submit():
        
        new_comment = Reviews(author_reviews=current_user, cafe_id=cafe_id , review=review_form.review.data)
        db.session.add(new_comment)
        db.session.commit()

    # requesting the cafe id by opening a session and just reading it
    request_cafe = db.session.query(Cafes).get(cafe_id)

    # bolding the current day of the week
    now = datetime.now()
    day_name = now.strftime("%A")

    return render_template('cafe.html', cafe=request_cafe, all_reviews=request_review, day_name=day_name, rating_form=rating_form, review_form=review_form, new_cafee=new_cafe, logged_in=current_user.is_authenticated)


@application.route('/add-cafe', methods=['GET', 'POST'])
@login_required
def add_cafe():
    new_cafe = NewCafeForm()
    if new_cafe.validate_on_submit():
        name = new_cafe.name.data
        map_url = new_cafe.map_url.data
        img_url = new_cafe.img_url.data
        location = new_cafe.location.data
        address = new_cafe.address.data
        has_sockets = new_cafe.has_sockets.data
        has_toilet = new_cafe.has_toilet.data
        has_wifi = new_cafe.has_wifi.data
        can_take_calls = new_cafe.can_take_calls.data
        seats = new_cafe.seats.data
        coffee_price = new_cafe.coffee_price.data

        new_cafe = Cafes(name=name, map_url=map_url, img_url=img_url,
                         location=location, address=address, has_sockets=has_sockets,
                         has_toilet=has_toilet, has_wifi=has_wifi,
                         can_take_calls=can_take_calls, seats=seats, coffee_price=coffee_price)

        db.session.add(new_cafe)
        db.session.commit()

        return redirect(url_for('home'))

    return render_template('add_cafe.html', new_cafee=new_cafe, logged_in=current_user.is_authenticated)


@application.route('/register', methods=['GET', 'POST'])
def register():
    register_form = RegisterForm()
    if register_form.validate_on_submit():
        name = register_form.name.data
        email = register_form.email.data
        password = register_form.password.data

        result = db.session.execute(
            db.select(Users).where(Users.email == email))
        user = result.scalar()

        if user:
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for('login'))

        hashed_password = generate_password_hash(
            password, method='pbkdf2')

        new_user = Users(name=name, email=email, password=hashed_password)

        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)

        return redirect(url_for('home'))

    return render_template('register.html', register_form=register_form, logged_in=current_user.is_authenticated)


@application.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        email = login_form.email.data
        password = login_form.password.data

        result = db.session.execute(
            db.select(Users).where(Users.email == email))
        user = result.scalar()
        
        if not user:
            flash("That email does not exist, please try again.")
            return redirect(url_for('login'))
        elif not check_password_hash(user.password, password):
            flash('Password incorrect, please try again.')
            return redirect(url_for('login'))
        else:
            login_user(user)
            return redirect(url_for('add_cafe'))

    return render_template('login.html', login_form=login_form, logged_in=current_user.is_authenticated)


@application.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


if __name__ == '__main__':
    application.run(debug=True)
