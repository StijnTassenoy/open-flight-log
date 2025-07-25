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
        """Returns the total number of flights recorded in the logbook."""
        _QUERY_GET_FLIGHT_COUNT = "SELECT COUNT(*) AS flight_count FROM flights"

        cursor = await cls._db.execute(_QUERY_GET_FLIGHT_COUNT)
        row = await cursor.fetchone()

        if row is None:
            return 0

        return row["flight_count"]

    @classmethod
    async def get_total_flight_time(cls) -> tuple[int, int]:
        """Calculates total flight time from the database."""
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
    async def dispose(cls):
        """ Closes the database connection. """
        if cls._db:
            await cls._db.close()
            cls._db = None
            LOGGER.debug("Database connection closed.")