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
    async def get_total_flight_time(cls) -> tuple[int, int]:
        """ Calculates total flight time from the database. """
        _QUERY_GET_SUM_OF_FLIGHT_TIME = """
            SELECT 
                COALESCE(SUM(total_flight_time_hrs), 0),
                COALESCE(SUM(total_flight_time_min), 0)
            FROM flights
        """
        cursor = await cls._db.execute(_QUERY_GET_SUM_OF_FLIGHT_TIME)
        row = await cursor.fetchone()
        hrs, mins = row[0], row[1]

        # Normalize minutes into hours
        total_hrs = hrs + (mins // 60)
        total_mins = mins % 60

        return total_hrs, total_mins

    @classmethod
    async def get_most_flown_aircraft(cls) -> str:
        """ Returns the aircraft type with the most total flight time (hours + minutes combined). """
        _QUERY_MOST_FLOWN = """
            SELECT aircraft_type,
                   SUM(COALESCE(total_flight_time_hrs, 0) * 60 + COALESCE(total_flight_time_min, 0)) AS total_minutes
            FROM flights
            WHERE aircraft_type IS NOT NULL
            GROUP BY aircraft_type
            ORDER BY total_minutes DESC
            LIMIT 1
        """

        cursor = await cls._db.execute(_QUERY_MOST_FLOWN)
        row = await cursor.fetchone()

        if row is None:
            return "N/A"

        return row["aircraft_type"]

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
        insert_query = """
            INSERT INTO flights (
                date, dept_place, dept_time, arrv_place, arrv_time,
                aircraft_type, aircraft_registration, single_pilot_time,
                multi_pilot_time_hrs, multi_pilot_time_min,
                total_flight_time_hrs, total_flight_time_min,
                pilot_in_command, landings_day, landings_night,
                oct_night_hrs, oct_night_min, oct_ifr_hrs, oct_ifr_mins,
                pft_pic_hrs, pft_pic_min, pft_copilot_hrs, pft_copilot_min,
                pft_dual_hrs, pft_dual_min, pft_instructor_hrs, pft_instructor_min,
                fstd_date, fstd_type, fstd_total_time_sess_hrs, fstd_total_time_sess_min,
                remarks
            ) VALUES (
                ?, ?, ?, ?, ?,
                ?, ?, ?,
                ?, ?,
                ?, ?,
                ?, ?, ?,
                ?, ?, ?, ?,
                ?, ?, ?, ?,
                ?, ?, ?, ?,
                ?, ?, ?, ?,
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
            flight_data.get("multi_pilot_time_hrs"),
            flight_data["multi_pilot_time_min"],
            flight_data.get("total_flight_time_hrs"),
            flight_data["total_flight_time_min"],
            flight_data["pilot_in_command"],
            flight_data.get("landings_day"),
            flight_data.get("landings_night"),
            flight_data.get("oct_night_hrs"),
            flight_data["oct_night_min"],
            flight_data.get("oct_ifr_hrs"),
            flight_data["oct_ifr_mins"],
            flight_data.get("pft_pic_hrs"),
            flight_data["pft_pic_min"],
            flight_data.get("pft_copilot_hrs"),
            flight_data.get("pft_copilot_min"),
            flight_data.get("pft_dual_hrs"),
            flight_data.get("pft_dual_min"),
            flight_data.get("pft_instructor_hrs"),
            flight_data.get("pft_instructor_min"),
            flight_data.get("fstd_date"),
            flight_data.get("fstd_type"),
            flight_data.get("fstd_total_time_sess_hrs"),
            flight_data.get("fstd_total_time_sess_min"),
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