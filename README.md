# Fire Safety Management System (ГДПБЗН)

A learning project — a web application that supports the daily operations of a
fire department: registering incidents, managing teams and staff, distributing
tasks and resources, and chat per incident.

## Tech stack

- **Python + Flask** — server and logic
- **SQLite** — database
- **HTML + CSS + JavaScript** — interface
- **Leaflet + OpenStreetMap** — map for the incident GPS point

## Project structure
```
├── run.py                  # start the server
├── config.py               # settings (database path lives here)
├── requirements.txt        # libraries
├── database/
│   ├── schema.sql          # tables
│   ├── seed.sql            # base data (vehicles, templates)
│   └── init_db.py          # optional manual rebuild
├── app/
│   ├── __init__.py     # application factory + blueprint registration
│   ├── db.py               # database helper functions
│   ├── seed.py             # builds the database + demo data
│   ├── auth_utils.py       # login and access control (roles)
│   ├── chat_reads.py       # chat "seen" receipts
│   ├── blueprints/         # the modules (one file per topic)
│   │   ├── public.py       # home + citizen report
│   │   ├── auth.py         # login / logout
│   │   ├── dashboard.py    # role-specific dashboard
│   │   ├── employees.py    # staff + vehicles
│   │   ├── incidents.py    # incidents + team + map
│   │   ├── tasks.py        # tasks
│   │   ├── resources.py    # resource requests
│   │   ├── messages.py     # per-incident chat
│   │   └── ops.py          # operations channel (staff <-> control room)
│   ├── templates/          # HTML pages
│   └── static/             # CSS, JS and the logo image
└── docs/
└── diagrams/           # block diagrams (.drawio)
```

## Running

```bash
# 1. Install the libraries
pip install -r requirements.txt

# 2. Start the server (the database is created automatically on first run)
python run.py
```

Then open in the browser: **http://127.0.0.1:5000**

To wipe and rebuild the database from scratch (optional):

```bash
python database/init_db.py
```

## Demo users (password for all: `1234`)

| User            | Role          | What they can do                                   |
|-----------------|---------------|----------------------------------------------------|
| `admin`         | administrator | manage staff, vehicles and roles                   |
| `dispatcher`    | dispatcher    | register incidents, assign teams, tasks, resources |
| `<second_name>` | firefighter   | any firefighter — the username is the person's surname in latin (lowercase); see their incidents/tasks, confirm, report, chat |

> There are many firefighters in the demo database, each logging in with their own surname.

## Roles

- **Citizen** (no login) — reports an incident.
- **Dispatcher** (control room) — registers incidents, sees staff statuses,
  assigns the team, creates tasks, approves resource requests.
- **Firefighter** — has a personal dashboard with their incidents, tasks, call
  history, a self status toggle, per-incident chat, and an operations channel to
  reach the control room.
- **Administrator** — manages staff and vehicles.

[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/RlRKNPRa)
