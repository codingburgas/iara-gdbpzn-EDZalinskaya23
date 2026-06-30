"""Incident management: list, create, detail (team/tasks/resources/chat),
assign staff, confirm and change status.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash

from app import db
from app.auth_utils import login_required, role_required, current_user

incidents_bp = Blueprint("incidents", __name__)

INCIDENT_TYPES = ["Пожар", "Авария", "ПТП", "Спасяване", "Друго"]
INCIDENT_STATUSES = ["Нова", "В процес", "Приключена"]

# Order in which staff categories appear in the assign dropdown
CATEGORY_ORDER = ["Командири", "Пожарникари", "Шофьори", "Спасители", "Други"]


def staff_category(position):
    """Map a job title to a category, to group people in the assign dropdown."""
    p = (position or "").lower()
    if "шоф" in p:
        return "Шофьори"
    if "спасител" in p:
        return "Спасители"
    if "командир" in p:
        return "Командири"
    if "пожарникар" in p:
        return "Пожарникари"
    return "Други"


@incidents_bp.route("/incidents")
@login_required
def list_incidents():
    incidents = db.query(
        """SELECT i.*,
                  (SELECT COUNT(*) FROM incident_assignments a WHERE a.incident_id = i.id) AS team_size
           FROM incidents i
           ORDER BY
               CASE i.status WHEN 'Нова' THEN 0 WHEN 'В процес' THEN 1 ELSE 2 END,
               i.created_at DESC"""
    )
    return render_template("incidents/list.html", incidents=incidents)


@incidents_bp.route("/incidents/new", methods=["GET", "POST"])
@role_required("dispatcher", "admin")
def create_incident():
    if request.method == "POST":
        itype = request.form.get("type", "").strip()
        address = request.form.get("address", "").strip()
        description = request.form.get("description", "").strip()
        channel = request.form.get("channel", "112")
        lat = request.form.get("lat") or None
        lng = request.form.get("lng") or None

        if not itype or not address:
            flash("Тип и адрес са задължителни.", "danger")
            return render_template("incidents/form.html", types=INCIDENT_TYPES)

        new_id = db.execute(
            """INSERT INTO incidents (type, address, lat, lng, description, channel, status, created_by)
               VALUES (?, ?, ?, ?, ?, ?, 'Нова', ?)""",
            (itype, address, lat, lng, description, channel, current_user()["id"]),
        )
        flash("Произшествието е създадено. Сега назначете екип.", "success")
        return redirect(url_for("incidents.incident_detail", incident_id=new_id))

    return render_template("incidents/form.html", types=INCIDENT_TYPES)


@incidents_bp.route("/incidents/<int:incident_id>")
@login_required
def incident_detail(incident_id):
    incident = db.query("SELECT * FROM incidents WHERE id = ?", (incident_id,), one=True)
    if incident is None:
        flash("Произшествието не е намерено.", "danger")
        return redirect(url_for("incidents.list_incidents"))

    # The assigned team
    team = db.query(
        """SELECT a.id AS assignment_id, a.confirmed, u.id AS user_id, u.full_name, u.position
           FROM incident_assignments a
           JOIN users u ON u.id = a.user_id
           WHERE a.incident_id = ?
           ORDER BY u.full_name""",
        (incident_id,),
    )

    # Firefighters not on the team: group available by category, keep the rest
    candidates = db.query(
        """SELECT * FROM users
           WHERE role = 'firefighter'
             AND id NOT IN (SELECT user_id FROM incident_assignments WHERE incident_id = ?)
           ORDER BY full_name""",
        (incident_id,),
    )
    groups = {c: [] for c in CATEGORY_ORDER}
    unavailable = []
    for person in candidates:
        if person["status"] == "Наличен":
            groups[staff_category(person["position"])].append(person)
        else:
            unavailable.append(person)
    # Only keep non-empty groups, in the defined order
    available_groups = [(cat, groups[cat]) for cat in CATEGORY_ORDER if groups[cat]]

    tasks = db.query(
        """SELECT t.*, u.full_name AS assignee
           FROM tasks t LEFT JOIN users u ON u.id = t.assigned_to
           WHERE t.incident_id = ? ORDER BY t.created_at""",
        (incident_id,),
    )
    resources = db.query(
        "SELECT * FROM resource_requests WHERE incident_id = ? ORDER BY created_at",
        (incident_id,),
    )
    messages = db.query(
        """SELECT m.*, u.full_name AS author
           FROM messages m LEFT JOIN users u ON u.id = m.user_id
           WHERE m.incident_id = ? ORDER BY m.created_at""",
        (incident_id,),
    )
    templates = db.query("SELECT * FROM message_templates ORDER BY id")

    # Current user's assignment, if any
    me = current_user()
    my_assignment = db.query(
        "SELECT * FROM incident_assignments WHERE incident_id = ? AND user_id = ?",
        (incident_id, me["id"]), one=True,
    )

    return render_template(
        "incidents/detail.html",
        incident=incident, team=team,
        available_groups=available_groups, unavailable=unavailable,
        tasks=tasks, resources=resources, messages=messages,
        templates=templates, my_assignment=my_assignment,
        statuses=INCIDENT_STATUSES,
    )


@incidents_bp.route("/incidents/<int:incident_id>/assign", methods=["POST"])
@role_required("dispatcher", "admin")
def assign_member(incident_id):
    user_id = request.form.get("user_id")
    if user_id:
        # Add to the team (INSERT OR IGNORE: UNIQUE constraint)
        db.execute(
            "INSERT OR IGNORE INTO incident_assignments (incident_id, user_id) VALUES (?, ?)",
            (incident_id, user_id),
        )
        # Mark the person as "На произшествие"
        db.execute("UPDATE users SET status = 'На произшествие' WHERE id = ?", (user_id,))
        flash("Служителят е назначен към произшествието.", "success")
    return redirect(url_for("incidents.incident_detail", incident_id=incident_id))


@incidents_bp.route("/incidents/<int:incident_id>/unassign/<int:user_id>", methods=["POST"])
@role_required("dispatcher", "admin")
def unassign_member(incident_id, user_id):
    db.execute(
        "DELETE FROM incident_assignments WHERE incident_id = ? AND user_id = ?",
        (incident_id, user_id),
    )
    # Set the person's status back to "Наличен"
    db.execute("UPDATE users SET status = 'Наличен' WHERE id = ?", (user_id,))
    flash("Служителят е премахнат от екипа.", "success")
    return redirect(url_for("incidents.incident_detail", incident_id=incident_id))


@incidents_bp.route("/incidents/<int:incident_id>/confirm", methods=["POST"])
@login_required
def confirm_assignment(incident_id):
    """A firefighter confirms they are taking the incident."""
    me = current_user()
    db.execute(
        "UPDATE incident_assignments SET confirmed = 1 WHERE incident_id = ? AND user_id = ?",
        (incident_id, me["id"]),
    )
    flash("Потвърдихте, че се заемате с произшествието.", "success")
    return redirect(url_for("incidents.incident_detail", incident_id=incident_id))


@incidents_bp.route("/incidents/<int:incident_id>/status", methods=["POST"])
@role_required("dispatcher", "admin")
def change_incident_status(incident_id):
    status = request.form.get("status")
    if status in INCIDENT_STATUSES:
        db.execute("UPDATE incidents SET status = ? WHERE id = ?", (status, incident_id))
        # When the incident is closed, free the team
        if status == "Приключена":
            db.execute(
                """UPDATE users SET status = 'Наличен'
                   WHERE id IN (SELECT user_id FROM incident_assignments WHERE incident_id = ?)""",
                (incident_id,),
            )
        flash("Статусът на произшествието е обновен.", "success")
    return redirect(url_for("incidents.incident_detail", incident_id=incident_id))
