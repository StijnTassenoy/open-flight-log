from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from starlette.templating import Jinja2Templates

from data.db import DB

router = APIRouter()
templates = Jinja2Templates(directory=".uv_templates")

@router.get("/flights", response_class=HTMLResponse)
async def get_flights(request: Request):
    rows = await DB.get_history()
    return templates.TemplateResponse("flights.html", {"request": request, "rows": rows})
