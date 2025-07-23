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
    async def dispose(cls):
        """ Closes the database connection. """
        if cls._db:
            await cls._db.close()
            cls._db = None
            LOGGER.debug("Database connection closed.")