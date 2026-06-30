"""Login and logout (for staff)."""
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash

from app import db

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        user = db.query("SELECT * FROM users WHERE username = ?", (username,), one=True)

        # Check that the user exists and the password matches
        if user is None or not check_password_hash(user["password_hash"], password):
            flash("Грешно потребителско име или парола.", "danger")
            return render_template("auth/login.html", username=username)

        # Store the id in the session to mark the user logged in
        session.clear()
        session["user_id"] = user["id"]
        flash(f"Успешен вход. Добре дошли, {user['full_name']}!", "success")
        return redirect(url_for("dashboard.index"))

    return render_template("auth/login.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("Излязохте от системата.", "success")
    return redirect(url_for("public.index"))
