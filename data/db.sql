-- flightlogbook.sql
-- SQLite schema for Open Flight Log

-- PRAGMA foreign_keys = ON;

-- Flights Table
CREATE TABLE flights (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    dept_place TEXT NOT NULL,
    dept_time TEXT NOT NULL,
    arrv_place TEXT NOT NULL,
    arrv_time TEXT NOT NULL,
    aircraft_type TEXT,
    aircraft_registration TEXT,
    single_pilot_time TEXT CHECK(single_pilot_time IN ('SE', 'ME')),
    multi_pilot_time TEXT,
    total_flight_time TEXT NOT NULL,
    pilot_in_command TEXT NOT NULL,
    landings_day INTEGER,
    landings_night INTEGER,
    oct_night TEXT,
    oct_ifr TEXT,
    pft_pic TEXT NOT NULL,
    pft_copilot TEXT,
    pft_dual TEXT,
    pft_instructor TEXT,
    fstd_date TEXT,
    fstd_type TEXT,
    fstd_total_time_sess TEXT,
    remarks TEXT
);