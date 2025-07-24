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
    arrv_time INT NOT NULL,
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
    oct_night_hrs INT,
    oct_night_min INT NOT NULL,
    oct_ifr_hrs INT,
    oct_ifr_mins INT NOT NULL,
    pft_pic_hrs INT,
    pft_pic_min INT NOT NULL,
    pft_copilot_hrs INT,
    pft_copilot_min INT,
    pft_dual_hrs INT,
    pft_dual_min INT,
    pft_instructor_hrs INT,
    pft_instructor_min INT,
    fstd_date DATE,
    fstd_type TEXT,
    fstd_total_time_sess_hrs INT,
    fstd_total_time_sess_min INT,
    remarks TEXT
);