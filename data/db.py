# Python Imports #
import os

# External Imports #
import aiofiles
import aiosqlite

# OFL Imports #
from lib.constants import DATABASE_FILE, SCHEMA_FILE
from lib.logger import LOGGER


class DB:
    _db: aiosqlite.Connection | None = None

    @classmethod
    async def initialize(cls):
        """ Initializes the database. If the DB file doesn't exist, it runs the schema creation SQL. """
        if cls._db is not None:
            return

        db_exists = os.path.exists(DATABASE_FILE)
        cls._db = await aiosqlite.connect(DATABASE_FILE)
        cls._db.row_factory = aiosqlite.Row  # Access rows like dicts

        if not db_exists:
            try:
                async with aiofiles.open(SCHEMA_FILE) as f:
                    schema_sql = await f.read()
                    await cls._db.executescript(schema_sql)
                    await cls._db.commit()
            except Exception as e:
                raise RuntimeError(f"Failed to initialize database schema: {e}")
    LOGGER.debug("Database connected.")

    @classmethod
    async def get_flights(cls) -> list[dict]:
        """ Returns all rows from the Flights table. """
        cursor = await cls._db.execute("SELECT * FROM flights")
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]

    @classmethod
    async def get_total_flight_count(cls) -> int:
        """ Returns the total number of flights recorded in the logbook. """
        _QUERY_GET_FLIGHT_COUNT = "SELECT COUNT(*) AS flight_count FROM flights"

        cursor = await cls._db.execute(_QUERY_GET_FLIGHT_COUNT)
        row = await cursor.fetchone()

        if row is None:
            return 0

        return row["flight_count"]

    @classmethod
    def _time_to_minutes(cls, time_str: str) -> int:
        """ Convert HH:MM string to total minutes. """
        if not time_str:
            return 0
        try:
            hours, minutes = map(int, time_str.split(':'))
            return hours * 60 + minutes
        except (ValueError, AttributeError):
            return 0

    @classmethod
    def _minutes_to_time(cls, minutes: int) -> str:
        """ Convert total minutes to HH:MM format. """
        if minutes is None or minutes == 0:
            return "00:00"
        hours = minutes // 60
        mins = minutes % 60
        return f"{hours:02d}:{mins:02d}"

    @classmethod
    async def get_total_flight_time(cls) -> tuple[int, int]:
        """ Calculates total flight time from the database. Returns (hours, minutes). """
        _QUERY_GET_ALL_FLIGHT_TIMES = "SELECT total_flight_time FROM flights WHERE total_flight_time IS NOT NULL"

        cursor = await cls._db.execute(_QUERY_GET_ALL_FLIGHT_TIMES)
        rows = await cursor.fetchall()

        total_minutes = sum(cls._time_to_minutes(row["total_flight_time"]) for row in rows)

        total_hrs = total_minutes // 60
        total_mins = total_minutes % 60

        return total_hrs, total_mins

    @classmethod
    async def get_most_flown_aircraft(cls) -> str:
        """ Returns the aircraft type with the most total flight time. """
        _QUERY_ALL_AIRCRAFT = """
                SELECT aircraft_type, total_flight_time
                FROM flights
                WHERE aircraft_type IS NOT NULL AND total_flight_time IS NOT NULL
            """

        cursor = await cls._db.execute(_QUERY_ALL_AIRCRAFT)
        rows = await cursor.fetchall()

        if not rows:
            return "N/A"

        # Sum flight times per aircraft type
        aircraft_times = {}
        for row in rows:
            aircraft = row["aircraft_type"]
            minutes = cls._time_to_minutes(row["total_flight_time"])
            aircraft_times[aircraft] = aircraft_times.get(aircraft, 0) + minutes

        # Find aircraft with most time
        most_flown = max(aircraft_times.items(), key=lambda x: x[1])
        return most_flown[0]

    @classmethod
    async def get_last_flight(cls) -> dict:
        """ Returns the most recent flight entry based on the flight date. """
        _QUERY_LAST_FLIGHT = """
            SELECT *
            FROM flights
            ORDER BY date DESC, id DESC
            LIMIT 1
        """

        cursor = await cls._db.execute(_QUERY_LAST_FLIGHT)
        row = await cursor.fetchone()

        if row is None:
            return {}

        return dict(row)

    @classmethod
    async def insert_flight(cls, flight_data: dict):
        """ Insert a new flight record into the database. """
        insert_query = """
                INSERT INTO flights (
                    date, dept_place, dept_time, arrv_place, arrv_time,
                    aircraft_type, aircraft_registration, single_pilot_time,
                    multi_pilot_time, total_flight_time,
                    pilot_in_command, landings_day, landings_night,
                    oct_night, oct_ifr,
                    pft_pic, pft_copilot, pft_dual, pft_instructor,
                    fstd_date, fstd_type, fstd_total_time_sess,
                    remarks
                ) VALUES (
                    ?, ?, ?, ?, ?,
                    ?, ?, ?,
                    ?, ?,
                    ?, ?, ?,
                    ?, ?,
                    ?, ?, ?, ?,
                    ?, ?, ?,
                    ?
                )
            """

        values = (
            flight_data["date"],
            flight_data["dept_place"],
            flight_data["dept_time"],
            flight_data["arrv_place"],
            flight_data["arrv_time"],
            flight_data.get("aircraft_type"),
            flight_data.get("aircraft_registration"),
            flight_data.get("single_pilot_time"),
            flight_data.get("multi_pilot_time"),
            flight_data.get("total_flight_time"),
            flight_data["pilot_in_command"],
            flight_data.get("landings_day"),
            flight_data.get("landings_night"),
            flight_data.get("oct_night"),
            flight_data.get("oct_ifr"),
            flight_data.get("pft_pic"),
            flight_data.get("pft_copilot"),
            flight_data.get("pft_dual"),
            flight_data.get("pft_instructor"),
            flight_data.get("fstd_date"),
            flight_data.get("fstd_type"),
            flight_data.get("fstd_total_time_sess"),
            flight_data.get("remarks"),
        )

        await cls._db.execute(insert_query, values)
        await cls._db.commit()

    @classmethod
    async def dispose(cls):
        """ Closes the database connection. """
        if cls._db:
            await cls._db.close()
            cls._db = None
            LOGGER.debug("Database connection closed.")