-- flightlogbook.sql
-- SQLite schema for Open Flight Log

-- PRAGMA foreign_keys = ON;

-- Flights Table
CREATE TABLE flights (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE NOT NULL,
    departure TEXT NOT NULL,
    arrival TEXT NOT NULL,
    aircraft_type TEXT,
    aircraft_registration TEXT,
    stick_time REAL CHECK(stick_time >= 0),
    pilot_in_command TEXT,
    remarks TEXT
);