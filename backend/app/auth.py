
from flask import Blueprint, flash, render_template, redirect, url_for, request
from . import db
from .models import User
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import re

# Initialize Blueprint
auth = Blueprint("auth", __name__)

@auth.route("/")
def main():
    return render_template("base.html", user=current_user)

@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("log-email")
        password = request.form.get("log-password")
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
                flash("Logged in successfully.")
                login_user(user, remember=True)
                return redirect(url_for("views.home"))
        else:
            flash("Invalid username or password.", category="error")
    return render_template("login.html", user=current_user)

@auth.route("/signup", methods=["GET", "POST"])
def sign_up():
    if request.method == "POST":
        image = request.files["image"]
        filename = secure_filename(image.filename)
        mimetype_profile = image.mimetype
        email = request.form.get("sign-email")
        username = request.form.get("sign-username")
        password1 = request.form.get("sign-password1")
        password2 = request.form.get("sign-password2")
        is_creator = request.form.get("is_creator") == "on"

        validation_error= validate_user_data(email, username, password1, password2, image)
        if validation_error:
            flash(validation_error, category="error")
        else:

            # Assuming you handle the password hashing inside the User model
            new_user = User(
                username=username, 
                name=filename,
                email=email, 
                password=password1,  # This will trigger the password setter in the User model
                is_creator=is_creator,  # Ensure this is the correct field name as per your User model
                image=image.read(),         # Store the filename, handle file saving separately if needed
                mimetype_profile=mimetype_profile
            )
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash("User created successfully.")
            return redirect(url_for("views.home"))

    return render_template("signup.html", user=current_user)

@auth.route("/admin", methods=["GET", "POST"])
def admin():
    predefine_password = os.environ.get("ADMIN_PASSWORD", "default_admin_password")

    if request.method == "POST":
        email = request.form.get("log-email")
        password = request.form.get("log-password")
        Admin_password = request.form.get("log-ad-password")

        if email and password:
            admin = User.query.filter_by(email=email).first()
            if admin and admin.check_password(password):  # Use the check_password method
                if Admin_password == predefine_password:
                    flash("Logged in as admin.")
                    login_user(admin, remember=True)
                    return redirect(url_for("views.home"))
                else:
                    flash("Incorrect admin password.", category="error")
            else:
                flash("Invalid login credentials.", category="error")
        else:
            # Admin registration logic
            email = request.form.get("sign-email")
            username = request.form.get("sign-username")
            password = request.form.get("sign-password")
            Admin_password = request.form.get("sign-ad-password")
            image = request.files["image"]
            filename = secure_filename(image.filename)
            mimetype_profile = image.mimetype

            validation_error = validate_user_data(email, username, password, password, image, True)
            if validation_error:
                flash(validation_error, category="error")
            else:
                new_admin = User(image=image.read(), mimetype_profile=mimetype_profile, name=filename,
                                email=email, username=username, password=password, is_admin=True)
                db.session.add(new_admin)
                db.session.commit()
                login_user(new_admin, remember=True)
                flash("Admin account created.")
                return redirect(url_for("views.home"))

    return render_template("admin.html", user=current_user)

@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("views.home"))

def validate_user_data(email, username, password1, password2, image, admin=False):
    if not image:
        return "No profile image selected.", None
    if User.query.filter_by(email=email).first():
        return "Email is already in use.", None
    if User.query.filter_by(username=username).first():
        return "Username is already in use.", None
    if password1 != password2:
        return "Passwords do not match.", None
    if len(username) < 2:
        return "Username is too short.", None
    if len(password1) < 6:
        return "Password is too short.", None
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return "Invalid email format.", None
    if admin and len(password1) < 8:
        return "Admin password is too short.", None
    return None