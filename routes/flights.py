# External Imports #
from fastapi import APIRouter, Request, Form, Depends
from fastapi.exceptions import HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse
from starlette.status import HTTP_303_SEE_OTHER
from starlette.templating import Jinja2Templates

# OFL Imports #
from data.db import DB
from lib.validation import FlightForm
from lib.security import validate_csrf

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
    csrf_token: str = Depends(validate_csrf),
    date: str = Form(...),
    dept_place: str = Form(...),
    dept_time: str = Form(...),
    arrv_place: str = Form(...),
    arrv_time: str = Form(...),
    aircraft_type: str = Form(None),
    aircraft_registration: str = Form(None),
    single_pilot_time: str = Form(None),
    multi_pilot_time: str = Form(None),
    total_flight_time: str = Form(...),
    pilot_in_command: str = Form(...),
    landings_day: str = Form(None),
    landings_night: str = Form(None),
    oct_night: str = Form(None),
    oct_ifr: str = Form(None),
    pft_pic: str = Form(...),
    pft_copilot: str = Form(None),
    pft_dual: str = Form(None),
    pft_instructor: str = Form(None),
    fstd_date: str = Form(None),
    fstd_type: str = Form(None),
    fstd_total_time_sess: str = Form(None),
    remarks: str = Form(None),
):
    payload = {
        "date": date,
        "dept_place": dept_place,
        "dept_time": dept_time,
        "arrv_place": arrv_place,
        "arrv_time": arrv_time,
        "aircraft_type": aircraft_type,
        "aircraft_registration": aircraft_registration,
        "single_pilot_time": single_pilot_time,
        "multi_pilot_time": multi_pilot_time,
        "total_flight_time": total_flight_time,
        "pilot_in_command": pilot_in_command,
        "landings_day": landings_day,
        "landings_night": landings_night,
        "oct_night": oct_night,
        "oct_ifr": oct_ifr,
        "pft_pic": pft_pic,
        "pft_copilot": pft_copilot,
        "pft_dual": pft_dual,
        "pft_instructor": pft_instructor,
        "fstd_date": fstd_date,
        "fstd_type": fstd_type,
        "fstd_total_time_sess": fstd_total_time_sess,
        "remarks": remarks,
    }

    try:
        flight = FlightForm.model_validate(payload)
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))

    await DB.insert_flight(flight.model_dump())
    return RedirectResponse(url="/flights", status_code=HTTP_303_SEE_OTHER)