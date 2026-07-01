# Getting Started

## Requirements

- Python 3
- The libraries listed in `requirements.txt` (Flask and Werkzeug)

## Install and run

```bash
# 1. Install the libraries
pip install -r requirements.txt

# 2. Start the server (the database is created automatically on first run)
python run.py
```

Then open **http://127.0.0.1:5000** in a browser.

On the first run the application builds `database/gdpbzn.db` from `schema.sql` and
`seed.sql`, then adds the demo vehicles and users. On later runs the existing database
is reused.

## Rebuild the database

To wipe and rebuild the database from scratch:

```bash
python database/init_db.py
```

## Demo accounts

All demo accounts use the password `1234`.

| Username | Role |
|----------|------|
| `admin` | Administrator |
| `dispatcher` | Dispatcher |
| `<surname>` | Firefighter (e.g. `ivanov`, `petrov`) |

## First steps

1. Open the home page and submit a test signal as a citizen.
2. Log in as `dispatcher`, register or open an incident, and assign a team.
3. Log in as a firefighter, confirm participation, and use the incident chat.

See **[[Roles and Access]]** for what each role can do.
