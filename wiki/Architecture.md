# Architecture

## Request lifecycle

1. `run.py` calls `create_app()` and starts the development server.
2. `create_app()` (in `app/__init__.py`) configures the app, registers the database
   teardown hook, builds the database on first run, and registers all blueprints.
3. A request is routed to a view function inside a blueprint.
4. The view reads or writes data through the helpers in `app/db.py` and renders a
   Jinja2 template from `app/templates/`.
5. Static assets (CSS, JavaScript, the logo image) are served from `app/static/`.

## Application factory

`create_app()`:

- Loads settings from `config.Config`.
- Registers `db.close_db` so the SQLite connection closes after every request.
- Builds the database on first run, then idempotently ensures the demo data exists.
- Registers the nine blueprints.
- Injects `current_user` and `role_labels` into every template via a context processor.

## Modules (blueprints)

| Blueprint | Responsibility |
|-----------|----------------|
| `public` | Home page and the citizen report form (no login). |
| `auth` | Staff login and logout. |
| `dashboard` | Role-specific overview and the operations channel. |
| `employees` | Staff and vehicle management. |
| `incidents` | Incidents: list, create, detail, team assignment, status. |
| `tasks` | Tasks per incident. |
| `resources` | Resource requests per incident. |
| `messages` | Per-incident chat (post + JSON feed). |
| `ops` | Operations channel (shared chat). |

## Database access layer

`app/db.py` provides a small interface used everywhere:

- `get_db()` — a per-request SQLite connection (rows by name, foreign keys on).
- `query(sql, params, one)` — SELECT.
- `execute(sql, params)` — INSERT/UPDATE/DELETE, commit, return new id.

## Live chat

The per-incident chat and the operations channel both refresh by polling a JSON
endpoint every few seconds (`app/static/js/chat.js`). Read receipts are stored in the
`chat_reads` table, which powers the "seen by" line.

## Directory structure

```
├── run.py                  # starts the server
├── config.py               # settings (database path, secret key)
├── requirements.txt
├── database/               # schema.sql, seed.sql, init_db.py, gdpbzn.db
├── app/
│   ├── __init__.py         # application factory + blueprint registration
│   ├── db.py               # database helpers
│   ├── seed.py             # builds the database + demo data
│   ├── auth_utils.py       # login and access control
│   ├── chat_reads.py       # chat "seen" receipts
│   ├── blueprints/         # one module per topic
│   ├── templates/          # Jinja2 pages
│   └── static/             # CSS, JS, logo
└── docs/diagrams/          # .drawio diagrams
```

See the `docs/diagrams/architecture.drawio` file for the visual version.
