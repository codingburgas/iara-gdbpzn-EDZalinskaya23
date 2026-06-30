"""Management of staff and vehicles.

Access: admin (full) and dispatcher (view + status change).
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash

from app import db
from app.auth_utils import role_required

employees_bp = Blueprint("employees", __name__)

# Staff statuses, kept in one place (Bulgarian: shown in the UI)
STATUSES = ["Наличен", "Почивка", "На произшествие", "Отпуск", "Болничен", "Командировка"]
ROLES = ["firefighter", "dispatcher", "admin"]


@employees_bp.route("/employees")
@role_required("admin", "dispatcher")
def list_employees():
    employees = db.query(
        """SELECT u.*, v.name AS vehicle_name
           FROM users u
           LEFT JOIN vehicles v ON v.id = u.vehicle_id
           ORDER BY u.full_name"""
    )
    vehicles = db.query("SELECT * FROM vehicles ORDER BY name")
    return render_template("employees/list.html",
                           employees=employees, vehicles=vehicles,
                           statuses=STATUSES)


@employees_bp.route("/employees/new", methods=["GET", "POST"])
@role_required("admin")
def create_employee():
    vehicles = db.query("SELECT * FROM vehicles ORDER BY name")
    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        role = request.form.get("role", "firefighter")
        position = request.form.get("position", "").strip()
        phone = request.form.get("phone", "").strip()
        vehicle_id = request.form.get("vehicle_id") or None

        if not full_name or not username or not password:
            flash("Име, потребителско име и парола са задължителни.", "danger")
            return render_template("employees/form.html", vehicles=vehicles,
                                   roles=ROLES, employee=None)

        # Check for a taken username
        if db.query("SELECT 1 FROM users WHERE username = ?", (username,), one=True):
            flash("Това потребителско име вече съществува.", "danger")
            return render_template("employees/form.html", vehicles=vehicles,
                                   roles=ROLES, employee=None)

        db.execute(
            """INSERT INTO users (full_name, username, password_hash, role, position, phone, vehicle_id)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (full_name, username, generate_password_hash(password), role, position, phone, vehicle_id),
        )
        flash("Служителят е добавен.", "success")
        return redirect(url_for("employees.list_employees"))

    return render_template("employees/form.html", vehicles=vehicles,
                           roles=ROLES, employee=None)


@employees_bp.route("/employees/<int:user_id>/edit", methods=["GET", "POST"])
@role_required("admin")
def edit_employee(user_id):
    employee = db.query("SELECT * FROM users WHERE id = ?", (user_id,), one=True)
    if employee is None:
        flash("Служителят не е намерен.", "danger")
        return redirect(url_for("employees.list_employees"))

    vehicles = db.query("SELECT * FROM vehicles ORDER BY name")
    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        role = request.form.get("role", "firefighter")
        position = request.form.get("position", "").strip()
        phone = request.form.get("phone", "").strip()
        vehicle_id = request.form.get("vehicle_id") or None

        db.execute(
            """UPDATE users SET full_name = ?, role = ?, position = ?, phone = ?, vehicle_id = ?
               WHERE id = ?""",
            (full_name, role, position, phone, vehicle_id, user_id),
        )
        flash("Промените са запазени.", "success")
        return redirect(url_for("employees.list_employees"))

    return render_template("employees/form.html", vehicles=vehicles,
                           roles=ROLES, employee=employee)


@employees_bp.route("/employees/<int:user_id>/status", methods=["POST"])
@role_required("admin", "dispatcher")
def change_status(user_id):
    """Quick status change from the staff list."""
    status = request.form.get("status")
    if status in STATUSES:
        db.execute("UPDATE users SET status = ? WHERE id = ?", (status, user_id))
        flash("Статусът е обновен.", "success")
    return redirect(url_for("employees.list_employees"))


# Vehicles
@employees_bp.route("/vehicles", methods=["GET", "POST"])
@role_required("admin")
def vehicles():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        plate = request.form.get("plate", "").strip()
        vtype = request.form.get("type", "").strip()
        if name:
            db.execute("INSERT INTO vehicles (name, plate, type) VALUES (?, ?, ?)",
                       (name, plate, vtype))
            flash("Автомобилът е добавен.", "success")
        return redirect(url_for("employees.vehicles"))

    all_vehicles = db.query("SELECT * FROM vehicles ORDER BY name")
    return render_template("employees/vehicles.html", vehicles=all_vehicles)
