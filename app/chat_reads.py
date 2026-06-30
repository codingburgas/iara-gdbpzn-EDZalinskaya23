"""Chat read receipts ("seen"): track the highest message id each user has seen."""
from app import db


def mark_read(channel, channel_id, user_id, last_id):
    """Record that `user_id` has seen messages up to `last_id` in this channel."""
    if not last_id:
        return
    db.execute(
        """INSERT INTO chat_reads (channel, channel_id, user_id, last_read_id)
           VALUES (?, ?, ?, ?)
           ON CONFLICT(channel, channel_id, user_id)
           DO UPDATE SET last_read_id = excluded.last_read_id
           WHERE excluded.last_read_id > chat_reads.last_read_id""",
        (channel, channel_id, user_id, last_id),
    )


def seen_names(channel, channel_id, last_id, exclude_user_id):
    """Names of users who have seen the latest message (excluding its author)."""
    if not last_id:
        return []
    rows = db.query(
        """SELECT u.full_name
           FROM chat_reads r JOIN users u ON u.id = r.user_id
           WHERE r.channel = ? AND r.channel_id = ?
             AND r.last_read_id >= ?
             AND r.user_id != ?
           ORDER BY u.full_name""",
        (channel, channel_id, last_id, exclude_user_id or -1),
    )
    return [r["full_name"] for r in rows]
