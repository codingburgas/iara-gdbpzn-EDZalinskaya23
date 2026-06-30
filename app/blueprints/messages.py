"""Per-incident chat: post messages and serve the JSON feed used by live polling."""
from flask import Blueprint, request, redirect, url_for, flash, jsonify

from app import db, chat_reads
from app.auth_utils import login_required, current_user

messages_bp = Blueprint("messages", __name__)


@messages_bp.route("/incidents/<int:incident_id>/messages/add", methods=["POST"])
@login_required
def add_message(incident_id):
    body = request.form.get("body", "").strip()
    if body:
        db.execute(
            "INSERT INTO messages (incident_id, user_id, body) VALUES (?, ?, ?)",
            (incident_id, current_user()["id"], body),
        )
    else:
        flash("Празно съобщение не се изпраща.", "warning")
    return redirect(url_for("incidents.incident_detail", incident_id=incident_id) + "#chat")


@messages_bp.route("/incidents/<int:incident_id>/messages.json")
@login_required
def incident_messages_json(incident_id):
    """JSON feed of an incident's chat, used by the live chat (polling)."""
    rows = db.query(
        """SELECT m.id, m.user_id, m.body, m.created_at, u.full_name AS author
           FROM messages m LEFT JOIN users u ON u.id = m.user_id
           WHERE m.incident_id = ? ORDER BY m.created_at, m.id""",
        (incident_id,),
    )

    me = current_user()["id"]
    last_id = rows[-1]["id"] if rows else 0
    last_author = rows[-1]["user_id"] if rows else None

    # Mark the current user as having seen the latest message
    chat_reads.mark_read("incident", incident_id, me, last_id)
    seen = chat_reads.seen_names("incident", incident_id, last_id, last_author)

    return jsonify({
        "messages": [
            {"author": r["author"] or "Система", "body": r["body"], "created_at": r["created_at"]}
            for r in rows
        ],
        "seen_by": seen,
    })
