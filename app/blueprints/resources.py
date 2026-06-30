"""Resource requests per incident: anyone requests; the dispatcher moves status Заявена -> Одобрена -> Доставена."""
from flask import Blueprint, request, redirect, url_for, flash

from app import db
from app.auth_utils import login_required, role_required, current_user

resources_bp = Blueprint("resources", __name__)

RESOURCE_STATUSES = ["Заявена", "Одобрена", "Доставена"]


@resources_bp.route("/incidents/<int:incident_id>/resources/add", methods=["POST"])
@login_required
def add_resource(incident_id):
    resource_type = request.form.get("resource_type", "").strip()
    description = request.form.get("description", "").strip()

    if not resource_type:
        flash("Видът на ресурса е задължителен.", "danger")
    else:
        db.execute(
            """INSERT INTO resource_requests (incident_id, requested_by, resource_type, description, status)
               VALUES (?, ?, ?, ?, 'Заявена')""",
            (incident_id, current_user()["id"], resource_type, description),
        )
        flash("Заявката за ресурс е подадена.", "success")
    return redirect(url_for("incidents.incident_detail", incident_id=incident_id))


@resources_bp.route("/resources/<int:request_id>/status", methods=["POST"])
@role_required("dispatcher", "admin")
def update_resource_status(request_id):
    req = db.query("SELECT * FROM resource_requests WHERE id = ?", (request_id,), one=True)
    if req is None:
        flash("Заявката не е намерена.", "danger")
        return redirect(url_for("incidents.list_incidents"))

    status = request.form.get("status")
    if status in RESOURCE_STATUSES:
        db.execute("UPDATE resource_requests SET status = ? WHERE id = ?", (status, request_id))
        flash("Статусът на заявката е обновен.", "success")
    return redirect(url_for("incidents.incident_detail", incident_id=req["incident_id"]))
