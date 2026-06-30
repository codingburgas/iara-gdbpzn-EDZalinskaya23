"""Dashboard (after login): role-specific overview plus the operations channel."""
from flask import Blueprint, render_template, request, redirect, url_for, flash

from app import db
from app.auth_utils import login_required, current_user

dashboard_bp = Blueprint("dashboard", __name__)

# Statuses a firefighter may set on themselves (a safe subset)
SELF_STATUSES = ["Наличен", "Почивка"]


@dashboard_bp.route("/dashboard")
@login_required
def index():
    user = current_user()

    # Operations channel: last messages, newest at the bottom
    ops_messages = db.query(
        """SELECT m.*, u.full_name AS author
           FROM ops_messages m LEFT JOIN users u ON u.id = m.user_id
           ORDER BY m.created_at DESC LIMIT 30"""
    )
    ops_messages = list(reversed(ops_messages))

    # Ready-made message templates for quick replies
    templates = db.query("SELECT * FROM message_templates ORDER BY id")

    # Data for dispatcher / admin
    active_incidents = 0
    available_staff = 0
    # Data for firefighter
    my_incidents = []
    my_tasks = []
    history = []

    if user["role"] == "firefighter":
        my_incidents = db.query(
            """SELECT i.*, a.confirmed
               FROM incidents i
               JOIN incident_assignments a ON a.incident_id = i.id
               WHERE a.user_id = ? AND i.status != 'Приключена'
               ORDER BY i.created_at DESC""",
            (user["id"],),
        )
        my_tasks = db.query(
            """SELECT t.*, i.type AS incident_type, i.address
               FROM tasks t JOIN incidents i ON i.id = t.incident_id
               WHERE t.assigned_to = ? AND t.status != 'Приключена'
               ORDER BY t.created_at""",
            (user["id"],),
        )
        history = db.query(
            """SELECT i.*
               FROM incidents i
               JOIN incident_assignments a ON a.incident_id = i.id
               WHERE a.user_id = ? AND i.status = 'Приключена'
               ORDER BY i.created_at DESC LIMIT 10""",
            (user["id"],),
        )
    else:
        active_incidents = db.query(
            "SELECT COUNT(*) AS c FROM incidents WHERE status != 'Приключена'", one=True
        )["c"]
        available_staff = db.query(
            "SELECT COUNT(*) AS c FROM users WHERE status = 'Наличен' AND role = 'firefighter'",
            one=True,
        )["c"]

    return render_template(
        "dashboard/index.html",
        active_incidents=active_incidents,
        available_staff=available_staff,
        my_incidents=my_incidents,
        my_tasks=my_tasks,
        history=history,
        ops_messages=ops_messages,
        templates=templates,
        self_statuses=SELF_STATUSES,
    )


@dashboard_bp.route("/me/status", methods=["POST"])
@login_required
def set_my_status():
    """Let a logged-in user set their own status (limited to a safe subset)."""
    status = request.form.get("status")
    if status in SELF_STATUSES:
        db.execute("UPDATE users SET status = ? WHERE id = ?", (status, current_user()["id"]))
        flash("Статусът ви е обновен.", "success")
    return redirect(url_for("dashboard.index"))
