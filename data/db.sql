-- flightlogbook.sql
-- SQLite schema for Open Flight Log

-- PRAGMA foreign_keys = ON;

-- Flights Table
CREATE TABLE flights (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE NOT NULL,
    dept_place TEXT NOT NULL,
    dept_time INT NOT NULL,
    arrv_place TEXT NOT NULL,
    arrv_time TEXT INT NULL,
    aircraft_type TEXT,
    aircraft_registration TEXT,
    single_pilot_time TEXT CHECK(single_pilot_time IN ('SE', 'ME')),
    multi_pilot_time_hrs INT,
    multi_pilot_time_min INT NOT NULL,
    total_flight_time_hrs INT,
    total_flight_time_min INT NOT NULL,
    pilot_in_command TEXT NOT NULL,
    landings_day INT,
    landings_night INT,
    remarks TEXT
);