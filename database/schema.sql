-- Drop tables for a clean rebuild
DROP TABLE IF EXISTS chat_reads;
DROP TABLE IF EXISTS ops_messages;
DROP TABLE IF EXISTS messages;
DROP TABLE IF EXISTS message_templates;
DROP TABLE IF EXISTS resource_requests;
DROP TABLE IF EXISTS tasks;
DROP TABLE IF EXISTS incident_assignments;
DROP TABLE IF EXISTS incidents;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS vehicles;

-- vehicles
CREATE TABLE vehicles (
    id    INTEGER PRIMARY KEY AUTOINCREMENT,
    name  TEXT NOT NULL,
    plate TEXT,
    type  TEXT
);

-- users (role: admin | dispatcher | firefighter)
CREATE TABLE users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name     TEXT NOT NULL,
    username      TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role          TEXT NOT NULL DEFAULT 'firefighter',
    position      TEXT,
    status        TEXT NOT NULL DEFAULT 'Наличен',
    phone         TEXT,
    vehicle_id    INTEGER,
    FOREIGN KEY (vehicle_id) REFERENCES vehicles (id) ON DELETE SET NULL
);

-- incidents (channel: 112 | Онлайн | Телефон; status: Нова | В процес | Приключена)
CREATE TABLE incidents (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    type        TEXT NOT NULL,
    address     TEXT NOT NULL,
    lat         REAL,
    lng         REAL,
    description TEXT,
    channel     TEXT NOT NULL DEFAULT '112',
    status      TEXT NOT NULL DEFAULT 'Нова',
    created_at  TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    created_by  INTEGER,
    FOREIGN KEY (created_by) REFERENCES users (id) ON DELETE SET NULL
);

-- incident_assignments: staff on an incident (confirmed: 0 = pending, 1 = accepted)
CREATE TABLE incident_assignments (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    incident_id INTEGER NOT NULL,
    user_id     INTEGER NOT NULL,
    confirmed   INTEGER NOT NULL DEFAULT 0,
    UNIQUE (incident_id, user_id),
    FOREIGN KEY (incident_id) REFERENCES incidents (id) ON DELETE CASCADE,
    FOREIGN KEY (user_id)     REFERENCES users (id)     ON DELETE CASCADE
);

-- tasks per incident (category: Оперативна | Логистична | Административна | Друга; status: Нова | В процес | Приключена)
CREATE TABLE tasks (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    incident_id INTEGER NOT NULL,
    assigned_to INTEGER,
    category    TEXT NOT NULL DEFAULT 'Оперативна',
    description TEXT NOT NULL,
    status      TEXT NOT NULL DEFAULT 'Нова',
    created_at  TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (incident_id) REFERENCES incidents (id) ON DELETE CASCADE,
    FOREIGN KEY (assigned_to) REFERENCES users (id)     ON DELETE SET NULL
);

-- resource_requests (status: Заявена | Одобрена | Доставена)
CREATE TABLE resource_requests (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    incident_id   INTEGER NOT NULL,
    requested_by  INTEGER,
    resource_type TEXT NOT NULL,
    description   TEXT,
    status        TEXT NOT NULL DEFAULT 'Заявена',
    created_at    TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (incident_id)  REFERENCES incidents (id) ON DELETE CASCADE,
    FOREIGN KEY (requested_by) REFERENCES users (id)     ON DELETE SET NULL
);

-- messages: chat tied to an incident
CREATE TABLE messages (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    incident_id INTEGER NOT NULL,
    user_id     INTEGER,
    body        TEXT NOT NULL,
    created_at  TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (incident_id) REFERENCES incidents (id) ON DELETE CASCADE,
    FOREIGN KEY (user_id)     REFERENCES users (id)     ON DELETE SET NULL
);

-- message_templates: ready-made chat replies
CREATE TABLE message_templates (
    id   INTEGER PRIMARY KEY AUTOINCREMENT,
    text TEXT NOT NULL
);

-- ops_messages: general staff/control-room chat (not tied to an incident)
CREATE TABLE ops_messages (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id    INTEGER,
    body       TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE SET NULL
);

-- chat_reads: "seen" receipts (channel 'incident' = incident id, 'ops' = 0)
CREATE TABLE chat_reads (
    channel      TEXT NOT NULL,
    channel_id   INTEGER NOT NULL,
    user_id      INTEGER NOT NULL,
    last_read_id INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (channel, channel_id, user_id)
);
