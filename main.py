from flask import Flask, request, session, render_template, redirect, url_for, flash, get_flashed_messages, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin, AnonymousUserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from os import path
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, join_room, leave_room, emit, send

app = Flask(__name__)
DB_NAME = "food.db"
app.config["SECRET_KEY"] = "weofhwefoihwoiefh"
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{DB_NAME}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
db.init_app(app)


def create_database(app):
    if not path.exists(DB_NAME):
        db.create_all(app=app)
        print("Database has been created")


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    username = db.Column(db.String(150))
    password = db.Column(db.String(100))


create_database(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.route('/')
@login_required
def home():
    return render_template("Home.html")


METHODS = ["GET", "POST"]


@app.route("/login", methods=METHODS)
def login():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password1')

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                login_user(user, remember=True)
                return redirect(url_for("home"))
            else:
                flash('Incorrect password! Please try again.', category="fail")
        else:
            flash("Account doesn't exist. Please register to continue.",
                  category="fail")

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get('email')
        username = request.form.get('username')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(email=email).first()
        if user:
            flash("Email has been registered already.", category="fail")
        elif len(email) < 4:
            flash("Email must be greater than 3 characters.", category="fail")
        elif len(username) < 2:
            flash("Username must be greater than 1 character.", category="fail")
        elif password1 != password2:
            flash("Passwords must match! Please try again.", category="fail")
        elif len(password1) < 8:
            flash("Password must be at least 8 characters.", category="fail")

        else:
            new_user = User(email=email, username=username, password=generate_password_hash(
                password1, method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            return redirect(url_for("home"))

    return render_template("register.html", user=current_user)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Successfully logged out!", category="success")
    return redirect(url_for("home"))


@app.route("/info")
def info():
    return render_template("AboutUs.html")


@app.route("/recipes")
def recipes():
    return render_template("recipes.html")


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
