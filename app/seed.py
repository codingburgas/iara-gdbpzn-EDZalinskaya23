import os
import sqlite3

from werkzeug.security import generate_password_hash

import config

# Demo data (single source of truth)

# (name, plate, type) — order defines vehicle ids 1..8
VEHICLES = [
    ("Автоцистерна 1",  "СА 1234 АА", "Автоцистерна"),
    ("Автоцистерна 2",  "СА 5678 ВВ", "Автоцистерна"),
    ("Автостълба",      "СА 9012 СС", "Автостълба"),
    ("Спасителен",      "СА 3456 DD", "Спасителен автомобил"),
    ("Автоцистерна 3",  "СА 7788 ЕЕ", "Автоцистерна"),
    ("Щабен автомобил", "СА 2200 КК", "Щабен автомобил"),
    ("Автоцистерна 4",  "СА 4455 ММ", "Автоцистерна"),
    ("Автостълба 2",    "СА 6677 НН", "Автостълба"),
]

# (full_name, username, role, position, status, phone, vehicle_id)
# Password for every demo user is "1234".
USERS = [
    ("Администратор",      "admin",      "admin",       "Администратор",          "Наличен",         "0888000001", None),
    ("Мария Иванова",      "dispatcher", "dispatcher",  "Оперативен дежурен",     "Наличен",         "0888000002", None),
    ("Иван Иванов",        "ivanov",     "firefighter", "Командир на отделение",  "Наличен",         "0888000003", 1),
    ("Петър Петров",       "petrov",     "firefighter", "Пожарникар",             "Наличен",         "0888000004", 1),
    ("Георги Георгиев",    "georgiev",   "firefighter", "Пожарникар-шофьор",      "Отпуск",          "0888000005", 2),
    ("Стефан Стоянов",     "stoyanov",   "dispatcher",  "Оперативен дежурен",     "Наличен",         "0888000006", None),
    ("Николай Колев",      "kolev",      "firefighter", "Командир на отделение",  "Наличен",         "0888000007", 2),
    ("Димитър Димитров",   "dimitrov",   "firefighter", "Пожарникар-шофьор",      "Наличен",         "0888000008", 2),
    ("Атанас Тодоров",     "todorov",    "firefighter", "Пожарникар",             "Наличен",         "0888000009", 3),
    ("Васил Василев",      "vasilev",    "firefighter", "Пожарникар",             "Почивка",         "0888000010", 3),
    ("Кирил Маринов",      "marinov",    "firefighter", "Пожарникар",             "Наличен",         "0888000011", 1),
    ("Йордан Петков",      "petkov",     "firefighter", "Пожарникар-шофьор",      "Болничен",        "0888000012", 4),
    ("Христо Ангелов",     "angelov",    "firefighter", "Спасител",               "Наличен",         "0888000013", 4),
    ("Емил Тошев",         "toshev",     "firefighter", "Спасител",               "Наличен",         "0888000014", 4),
    ("Борис Славов",       "slavov",     "firefighter", "Командир на отделение",  "Командировка",    "0888000015", 5),
    ("Любомир Райчев",     "raychev",    "firefighter", "Пожарникар",             "Наличен",         "0888000016", 5),
    ("Симеон Гочев",       "gochev",     "firefighter", "Пожарникар-шофьор",      "Наличен",         "0888000017", 5),
    ("Цветан Илиев",       "iliev",      "firefighter", "Пожарникар",             "Наличен",         "0888000018", 1),
    ("Радослав Пенев",     "penev",      "firefighter", "Пожарникар",             "Почивка",         "0888000019", 2),
    ("Александър Минчев",  "minchev",    "firefighter", "Пожарникар",             "Наличен",         "0888000020", 3),
    ("Пламен Драганов",    "draganov",   "firefighter", "Пожарникар",             "На произшествие", "0888000021", 1),
    ("Венелин Костов",     "kostov",     "firefighter", "Пожарникар",             "Отпуск",          "0888000022", 6),
    ("Десислава Петрова",  "admin2",     "admin",       "Системен администратор", "Наличен",         "0888000023", None),
    ("Галина Стефанова",   "stefanova",  "dispatcher",  "Оперативен дежурен",     "Наличен",         "0888000024", None),
    ("Тодор Иванов",       "tivanov",    "firefighter", "Командир на отделение",  "Наличен",         "0888000025", 7),
    ("Мирослав Геров",     "gerov",      "firefighter", "Пожарникар-шофьор",      "Наличен",         "0888000026", 7),
    ("Стоян Балев",        "balev",      "firefighter", "Пожарникар",             "Наличен",         "0888000027", 7),
    ("Ивайло Денев",       "denev",      "firefighter", "Пожарникар",             "Почивка",         "0888000028", 8),
    ("Калоян Манолов",     "manolov",    "firefighter", "Спасител",               "Наличен",         "0888000029", 8),
    ("Огнян Петров",       "opetrov",    "firefighter", "Пожарникар",             "Наличен",         "0888000030", 8),
    ("Деян Колев",         "dkolev",     "firefighter", "Пожарникар-шофьор",      "Болничен",        "0888000031", 4),
    ("Светослав Тонев",    "tonev",      "firefighter", "Пожарникар",             "Наличен",         "0888000032", 5),
    ("Захари Йорданов",    "zahariev",   "firefighter", "Пожарникар",             "Наличен",         "0888000033", 6),
    ("Филип Андонов",      "andonov",    "firefighter", "Пожарникар",             "Командировка",    "0888000034", 6),
    ("Мартин Збирков",     "zbirkov",    "firefighter", "Пожарникар",             "Наличен",         "0888000035", 3),
    ("Антон Грозев",       "grozev",     "firefighter", "Спасител",               "Наличен",         "0888000036", 4),
    ("Велизар Нинов",      "ninov",      "firefighter", "Пожарникар",             "Почивка",         "0888000037", 2),
    ("Боян Дочев",         "dochev",     "firefighter", "Пожарникар-шофьор",      "Наличен",         "0888000038", 1),
    ("Крум Лазаров",       "lazarov",    "firefighter", "Пожарникар",             "Наличен",         "0888000039", 7),
    ("Теодор Вълчев",      "valchev",    "firefighter", "Пожарникар",             "На произшествие", "0888000040", 8),
]


def _run_sql_file(conn, path):
    with open(path, "r", encoding="utf-8") as f:
        conn.executescript(f.read())


def has_tables():
    """Return True if the database already contains the 'users' table."""
    db_path = config.Config.DATABASE
    if not os.path.exists(db_path):
        return False
    conn = sqlite3.connect(db_path)
    row = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='users'"
    ).fetchone()
    conn.close()
    return row is not None


def ensure_demo_data():
    """Idempotently add any missing demo vehicles and users.

    Safe to run on every startup: existing rows are kept untouched.
    - vehicles: inserted only if a vehicle with the same name is missing
    - users:    INSERT OR IGNORE (username is UNIQUE)
    """
    conn = sqlite3.connect(config.Config.DATABASE)
    conn.execute("PRAGMA foreign_keys = ON")

    for name, plate, vtype in VEHICLES:
        conn.execute(
            """INSERT INTO vehicles (name, plate, type)
               SELECT ?, ?, ?
               WHERE NOT EXISTS (SELECT 1 FROM vehicles WHERE name = ?)""",
            (name, plate, vtype, name),
        )

    pw = generate_password_hash("1234")
    for full_name, username, role, position, status, phone, vehicle_id in USERS:
        conn.execute(
            """INSERT OR IGNORE INTO users
               (full_name, username, password_hash, role, position, status, phone, vehicle_id)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (full_name, username, pw, role, position, status, phone, vehicle_id),
        )

    conn.commit()
    conn.close()


def build_database():
    """Rebuild the database from scratch: schema + base data + demo data."""
    db_path = config.Config.DATABASE
    # Remove the old database file
    if os.path.exists(db_path):
        os.remove(db_path)

    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    # Create schema and base data
    _run_sql_file(conn, config.Config.SCHEMA_SQL)
    _run_sql_file(conn, config.Config.SEED_SQL)
    conn.commit()
    conn.close()

    # Add vehicles and users
    ensure_demo_data()

    # Insert a sample incident with team, tasks and a resource request
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute(
        """INSERT INTO incidents (type, address, lat, lng, description, channel, status, created_by)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        ("Пожар", "гр. София, ул. Витоша 10", 42.6934, 23.3200,
         "Запалена сграда в центъра.", "112", "В процес", 2),
    )
    conn.execute("INSERT INTO incident_assignments (incident_id, user_id, confirmed) VALUES (1, 3, 1)")
    conn.execute("INSERT INTO incident_assignments (incident_id, user_id, confirmed) VALUES (1, 4, 0)")
    conn.execute("INSERT INTO tasks (incident_id, assigned_to, category, description, status) VALUES (1, 3, 'Оперативна', 'Гасене от южната страна', 'В процес')")
    conn.execute("INSERT INTO tasks (incident_id, assigned_to, category, description, status) VALUES (1, 4, 'Логистична', 'Осигуряване на вода', 'Нова')")
    conn.execute("INSERT INTO resource_requests (incident_id, requested_by, resource_type, description, status) VALUES (1, 2, 'Цистерна с вода', 'Нужна е още една цистерна', 'Заявена')")
    # Per-incident chat starts empty (messages are filtered by incident_id)
    conn.commit()
    conn.close()
