"""Public pages (no login): home page and the citizen report form."""
from flask import Blueprint, render_template, request, flash

from app import db

public_bp = Blueprint("public", __name__)


@public_bp.route("/")
def index():
    """Home page."""
    return render_template("public/index.html")


@public_bp.route("/signal", methods=["GET", "POST"])
def report():
    """Form for a citizen to report an incident. Creates a new incident."""
    if request.method == "POST":
        incident_type = request.form.get("type", "").strip()
        address = request.form.get("address", "").strip()
        description = request.form.get("description", "").strip()
        # Optional GPS point, filled by the "use my location" button
        lat = request.form.get("lat") or None
        lng = request.form.get("lng") or None

        if not incident_type or not address:
            flash("Моля, попълнете тип и адрес на произшествието.", "danger")
            return render_template("public/report.html",
                                   type=incident_type, address=address,
                                   description=description, lat=lat, lng=lng)

        # Save the report as a new incident via the "Онлайн" channel
        db.execute(
            """INSERT INTO incidents (type, address, lat, lng, description, channel, status)
               VALUES (?, ?, ?, ?, ?, 'Онлайн', 'Нова')""",
            (incident_type, address, lat, lng, description),
        )
        return render_template("public/report_done.html")

    return render_template("public/report.html")
