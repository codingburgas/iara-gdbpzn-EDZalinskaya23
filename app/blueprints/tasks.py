"""Tasks per incident: the dispatcher adds and assigns them; status moves Нова -> В процес -> Приключена."""
from flask import Blueprint, request, redirect, url_for, flash

from app import db
from app.auth_utils import login_required, role_required

tasks_bp = Blueprint("tasks", __name__)

TASK_CATEGORIES = ["Оперативна", "Логистична", "Административна", "Друга"]
TASK_STATUSES = ["Нова", "В процес", "Приключена"]


@tasks_bp.route("/incidents/<int:incident_id>/tasks/add", methods=["POST"])
@role_required("dispatcher", "admin")
def add_task(incident_id):
    description = request.form.get("description", "").strip()
    category = request.form.get("category", "Оперативна")
    assigned_to = request.form.get("assigned_to") or None

    if not description:
        flash("Описанието на задачата е задължително.", "danger")
    else:
        if category not in TASK_CATEGORIES:
            category = "Оперативна"
        db.execute(
            """INSERT INTO tasks (incident_id, assigned_to, category, description, status)
               VALUES (?, ?, ?, ?, 'Нова')""",
            (incident_id, assigned_to, category, description),
        )
        flash("Задачата е добавена.", "success")
    return redirect(url_for("incidents.incident_detail", incident_id=incident_id))


@tasks_bp.route("/tasks/<int:task_id>/status", methods=["POST"])
@login_required
def update_task_status(task_id):
    task = db.query("SELECT * FROM tasks WHERE id = ?", (task_id,), one=True)
    if task is None:
        flash("Задачата не е намерена.", "danger")
        return redirect(url_for("incidents.list_incidents"))

    status = request.form.get("status")
    if status in TASK_STATUSES:
        db.execute("UPDATE tasks SET status = ? WHERE id = ?", (status, task_id))
        flash("Статусът на задачата е обновен.", "success")
    return redirect(url_for("incidents.incident_detail", incident_id=task["incident_id"]))
