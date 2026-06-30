"""Login and access control: current_user, login_required, role_required.

Roles: 'admin', 'dispatcher', 'firefighter'.
"""
from functools import wraps

from flask import g, redirect, session, url_for, flash

from app import db


def current_user():
    """Return the logged-in user's row from the DB, or None if not logged in."""
    if "user_id" not in session:
        return None
    # Cache the user in g to avoid repeat queries
    if "user" not in g:
        g.user = db.query(
            "SELECT * FROM users WHERE id = ?", (session["user_id"],), one=True
        )
    return g.user


def login_required(view):
    """Decorator: if no user is logged in -> redirect to the login page."""
    @wraps(view)
    def wrapped(*args, **kwargs):
        if current_user() is None:
            flash("Моля, влезте в системата.", "warning")
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)
    return wrapped


def role_required(*roles):
    """Decorator: allow only users whose role is in the given list."""
    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            user = current_user()
            if user is None:
                flash("Моля, влезте в системата.", "warning")
                return redirect(url_for("auth.login"))
            if user["role"] not in roles:
                flash("Нямате права за тази страница.", "danger")
                return redirect(url_for("dashboard.index"))
            return view(*args, **kwargs)
        return wrapped
    return decorator
