# External Imports #
from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from starlette.status import HTTP_303_SEE_OTHER
from starlette.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

# OFL Imports #
from data.db import DB

router = APIRouter()
templates = Jinja2Templates(directory=".uv_templates")

@router.get("/flights", response_class=HTMLResponse)
async def get_flights(request: Request):
    rows = await DB.get_flights()
    return templates.TemplateResponse("flights.html", {"request": request, "rows": rows})

@router.get("/flights/add")
async def new_flight_form(request: Request):
    return templates.TemplateResponse("add_flight.html", {"request": request})

@router.post("/flights/add")
async def create_flight(
    request: Request,
    date: str = Form(...),
    dept_place: str = Form(...),
    dept_time: str = Form(...),
    arrv_place: str = Form(...),
    arrv_time: str = Form(...),
    aircraft_type: str = Form(None),
    aircraft_registration: str = Form(None),
    single_pilot_time: str = Form(None),
    multi_pilot_time: str = Form(None),
    total_flight_time: str = Form(None),
    pilot_in_command: str = Form(...),
    landings_day: int = Form(None),
    landings_night: int = Form(None),
    oct_night: str = Form(None),
    oct_ifr: str = Form(None),
    pft_pic: str = Form(...),
    pft_copilot: str = Form(None),
    pft_dual: str = Form(None),
    pft_instructor: str = Form(None),
    fstd_date: str = Form(None),
    fstd_type: str = Form(None),
    fstd_total_time_sess: str = Form(None),
    remarks: str = Form(None)
):
    if aircraft_registration:
        aircraft_registration = aircraft_registration.upper()
    await DB.insert_flight(locals())
    return RedirectResponse(url="/flights", status_code=HTTP_303_SEE_OTHER)
