# External Imports #
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from starlette.templating import Jinja2Templates

# OFL Imports #
from data.db import DB

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
    return templates.TemplateResponse("index.html", {"request": request, "stats": stats})
