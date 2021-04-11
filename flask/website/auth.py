from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=["POST", "GET"])
def login():

    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password, try again!', category='error')
        else:
            flash('Email doesnt exist. Nice try!', category='error')

    return render_template("/login.html", user=current_user)


@auth.route('/logout')
@login_required
def logout():

    logout_user()
    return redirect(url_for('auth.login'))


@auth.route('/sign-up', methods=["GET", "POST"])
def sing_up():

    if request.method == "POST":

        email = request.form.get("email")
        first_name = request.form.get("firstName")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists!', category='error')
        elif len(email) < 4:
            flash("Email must be greater than 4 characters.", category='error')
        elif len(first_name) < 2:
            flash("I bet your first name is greater than 2 characters.", category='error')
        elif password1 != password2:
            flash("Your passwords don\'t match.", category='error')
        elif len(password1) < 7:
            flash("Your passwords is soo easy to crack less than 3 minutes. (at least 7 characters)", category='error')
        else:
            new_user = User(email=email, first_name=first_name,
                            password=generate_password_hash(password1, method='sha256'))
            user = new_user
            db.session.add(new_user)
            db.session.commit()
            try:
                login_user(user, remember=True)
                flash("[Account created] Welcome to main page", category='success')
                return redirect(url_for('views.home'))

            except AttributeError as err:
                flash("Something went wrong", category='error')
                return redirect(url_for('views.home'), user=current_user)

    return render_template("/sign_up.html", user=current_user)
