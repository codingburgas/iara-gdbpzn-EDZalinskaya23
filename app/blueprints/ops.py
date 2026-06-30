"""Operations channel: shared staff/control-room chat, not tied to an incident.

Handles posting and the JSON feed used by live polling.
"""
from flask import Blueprint, request, redirect, url_for, jsonify

from app import db, chat_reads
from app.auth_utils import login_required, current_user

ops_bp = Blueprint("ops", __name__)


@ops_bp.route("/ops/messages/add", methods=["POST"])
@login_required
def add_ops_message():
    body = request.form.get("body", "").strip()
    if body:
        db.execute(
            "INSERT INTO ops_messages (user_id, body) VALUES (?, ?)",
            (current_user()["id"], body),
        )
    return redirect(url_for("dashboard.index") + "#ops")


@ops_bp.route("/ops/messages.json")
@login_required
def ops_messages_json():
    """JSON feed of the operations channel, used by the live chat (polling)."""
    rows = db.query(
        """SELECT m.id, m.user_id, m.body, m.created_at, u.full_name AS author
           FROM ops_messages m LEFT JOIN users u ON u.id = m.user_id
           ORDER BY m.created_at DESC, m.id DESC LIMIT 30"""
    )
    # Query is newest-first (to take the last 30); flip to oldest-first for display
    rows = list(reversed(rows))

    me = current_user()["id"]
    last_id = rows[-1]["id"] if rows else 0
    last_author = rows[-1]["user_id"] if rows else None

    # Mark the current user as having seen the latest message
    chat_reads.mark_read("ops", 0, me, last_id)
    seen = chat_reads.seen_names("ops", 0, last_id, last_author)

    return jsonify({
        "messages": [
            {"author": r["author"] or "Система", "body": r["body"], "created_at": r["created_at"]}
            for r in rows
        ],
        "seen_by": seen,
    })
