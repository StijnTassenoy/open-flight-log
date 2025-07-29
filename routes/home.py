# Python imports #
import random

# External Imports #
import pandas as pd
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from starlette.templating import Jinja2Templates

# OFL Imports #
from data.db import DB
from lib.constants import QUOTES_FILE, CSV_SAVE_LOCATION
from lib.helpers import read_json_file

router = APIRouter()
templates = Jinja2Templates(directory=".uv_templates")

@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    total_flight_count = await DB.get_total_flight_count()
    total_flight_hrs, total_flight_min = await DB.get_total_flight_time()
    most_aircraft = await DB.get_most_flown_aircraft()
    last_flight_date = await DB.get_last_flight()
    stats = {
        "total_flights": total_flight_count,
        "total_hours": f"{total_flight_hrs}h {total_flight_min}min",
        "most_aircraft": most_aircraft,
        "last_flight": last_flight_date.get("date")
    }
    quote = await get_random_quote()
    return templates.TemplateResponse("index.html", {"request": request, "stats": stats, "quote": quote})

async def get_random_quote() -> str:
    """ Get random quote from json file. """
    try:
        quotes = await read_json_file(QUOTES_FILE)
        quotes = quotes.get("quotes")
        return random.choice(quotes) if quotes else "Clear skies ahead!"
    except Exception:
        return "Fly safe, pilot."

@router.get("/export", response_class=FileResponse)
async def export_csv():
    data = await DB.get_flights()
    df = pd.DataFrame(data)
    df.to_csv(CSV_SAVE_LOCATION, index=False)
    return FileResponse(path=CSV_SAVE_LOCATION, filename="flights_export.csv", media_type="text/csv")