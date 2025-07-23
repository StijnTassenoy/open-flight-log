from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from starlette.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory=".uv_templates")

@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    stats = {
        "total_flights": 42,
        "total_hours": 78.5,
        "most_aircraft": "Cessna 172",
        "last_flight": "2025-07-22"
    }
    return templates.TemplateResponse("index.html", {"request": request, "stats": stats})
