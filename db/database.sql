PRAGMA foreign_keys = ON;

-- 1. ROLES TABLE ---------------------------------------------------------
CREATE TABLE IF NOT EXISTS roles (
    role     TEXT PRIMARY KEY,
    sortkey  INTEGER NOT NULL
);

INSERT OR IGNORE INTO roles (role, sortkey) VALUES
('Administrator', 3),
('Manager',       2),
('User',          1);


-- 2. USERS TABLE ---------------------------------------------------------
-- Self-referencing manager_ID allows manager–employee hierarchy
CREATE TABLE IF NOT EXISTS users (
    user_ID     INTEGER PRIMARY KEY AUTOINCREMENT,
    username    TEXT UNIQUE,
    password    TEXT NOT NULL,
    email       TEXT,
    role        TEXT NOT NULL,
    manager_ID  INTEGER,
    FOREIGN KEY (role)       REFERENCES roles(role),
    FOREIGN KEY (manager_ID) REFERENCES users(user_ID) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS ix_users_role
    ON users(role);

CREATE INDEX IF NOT EXISTS ix_users_manager
    ON users(manager_ID);


-- 3. TRIPS TABLE ---------------------------------------------------------
CREATE TABLE IF NOT EXISTS trips (
    trip_ID     INTEGER PRIMARY KEY AUTOINCREMENT,
    destination TEXT NOT NULL,
    start_date  TEXT,
    end_date    TEXT,
    occasion    TEXT
);

CREATE INDEX IF NOT EXISTS ix_trips_start
    ON trips(start_date);


-- 4. USER_TRIPS (M:N USERS ↔ TRIPS) -------------------------------------
CREATE TABLE IF NOT EXISTS user_trips (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    trip_ID  INTEGER NOT NULL,
    user_ID  INTEGER NOT NULL,
    UNIQUE (user_ID, trip_ID),
    FOREIGN KEY (trip_ID) REFERENCES trips(trip_ID) ON DELETE CASCADE,
    FOREIGN KEY (user_ID) REFERENCES users(user_ID) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS ix_user_trips_trip
    ON user_trips(trip_ID);

CREATE INDEX IF NOT EXISTS ix_user_trips_user
    ON user_trips(user_ID);
