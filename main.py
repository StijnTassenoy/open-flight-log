# Python Imports #
from contextlib import asynccontextmanager

# External Imports #
import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# OFL Imports #
from data.db import DB
from lib.logger import LOGGER
from lib.constants import WELCOME_MESSAGE
from routes.home import router as home_router
from routes.flights import router as flights_router


# __ FastAPI __
@asynccontextmanager
async def lifespan(fastapi_app: FastAPI):
    # Startup Events
    LOGGER.info("Starting up Open Flight Log...")
    await DB.initialize()

    # Program during yield
    yield

    # Shutdown Events
    LOGGER.info("Shutting down Open Flight Log...")
    await DB.dispose()

app = FastAPI(title="Open Flight Log", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=".uv_static"), name="static")
templates = Jinja2Templates(directory=".uv_templates")

app.include_router(home_router)
app.include_router(flights_router)

def main():
    uvicorn.run("main:app", host="0.0.0.0", port=9966)

if __name__ == "__main__":
    print(WELCOME_MESSAGE)
    main()