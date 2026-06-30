"""SQLite helpers: get_db (connection), query (SELECT), execute (INSERT/UPDATE/DELETE)."""
import sqlite3

from flask import current_app, g


def get_db():
    """Return a DB connection. Cached in 'g' so we don't reopen it every time."""
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        # Access columns by name: row["name"]
        g.db.row_factory = sqlite3.Row
        # Enable foreign keys (off by default in SQLite)
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(exception=None):
    """Close the connection at the end of the request."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def query(sql, params=(), one=False):
    """Read data. one=True returns only the first row (or None)."""
    cur = get_db().execute(sql, params)
    rows = cur.fetchall()
    cur.close()
    return (rows[0] if rows else None) if one else rows


def execute(sql, params=()):
    """Run a change and commit. Returns the new row id (on INSERT)."""
    db = get_db()
    cur = db.execute(sql, params)
    db.commit()
    new_id = cur.lastrowid
    cur.close()
    return new_id


def init_app(app):
    """Hook closing the connection into the app lifecycle."""
    app.teardown_appcontext(close_db)
