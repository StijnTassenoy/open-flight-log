# Python Imports #
import re
from datetime import date as date_type
from typing import Optional

# External Imports #
from pydantic import BaseModel, Field, field_validator, model_validator

_HHMM_RE = re.compile(r"^(?:[0-1]\d|2[0-3]):[0-5]\d$")


def _normalize_time(value: Optional[str]) -> Optional[str]:
    """ Validate and normalize a HH:MM string, returning None for empty values. """
    if value is None:
        return None
    value = value.strip()
    if value == "":
        return None
    if not _HHMM_RE.match(value):
        raise ValueError("must be a valid HH:MM time (e.g. 01:30)")
    return value


class FlightForm(BaseModel):
    """ Validated representation of the /flights/add form submission. """

    date: date_type
    dept_place: str = Field(min_length=1, max_length=100)
    dept_time: Optional[str] = None
    arrv_place: str = Field(min_length=1, max_length=100)
    arrv_time: Optional[str] = None
    aircraft_type: Optional[str] = Field(default=None, max_length=100)
    aircraft_registration: Optional[str] = Field(default=None, max_length=20)
    single_pilot_time: Optional[str] = None
    multi_pilot_time: Optional[str] = None
    total_flight_time: str
    pilot_in_command: str = Field(min_length=1, max_length=100)
    landings_day: Optional[int] = Field(default=None, ge=0, le=1000)
    landings_night: Optional[int] = Field(default=None, ge=0, le=1000)
    oct_night: Optional[str] = None
    oct_ifr: Optional[str] = None
    pft_pic: str
    pft_copilot: Optional[str] = None
    pft_dual: Optional[str] = None
    pft_instructor: Optional[str] = None
    fstd_date: Optional[date_type] = None
    fstd_type: Optional[str] = Field(default=None, max_length=100)
    fstd_total_time_sess: Optional[str] = None
    remarks: Optional[str] = Field(default=None, max_length=2000)

    @field_validator("aircraft_registration")
    @classmethod
    def uppercase_registration(cls, v: Optional[str]) -> Optional[str]:
        if v:
            v = v.strip().upper()
        return v or None

    @field_validator("single_pilot_time")
    @classmethod
    def validate_single_pilot(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        v = v.strip()
        if v == "":
            return None
        if v not in ("SE", "ME"):
            raise ValueError("must be SE or ME")
        return v

    @field_validator(
        "dept_time", "arrv_time", "multi_pilot_time", "total_flight_time",
        "oct_night", "oct_ifr", "pft_pic", "pft_copilot", "pft_dual",
        "pft_instructor", "fstd_total_time_sess",
        mode="before",
    )
    @classmethod
    def validate_times(cls, v):
        return _normalize_time(v)

    @field_validator(
        "aircraft_type", "aircraft_registration", "single_pilot_time",
        "dept_place", "arrv_place", "pilot_in_command", "fstd_type", "remarks",
        mode="before",
    )
    @classmethod
    def blank_to_none_str(cls, v):
        if isinstance(v, str) and v.strip() == "":
            return None
        return v

    @field_validator(
        "date", "fstd_date", "landings_day", "landings_night",
        mode="before",
    )
    @classmethod
    def blank_to_none_other(cls, v):
        if isinstance(v, str) and v.strip() == "":
            return None
        return v

    @field_validator(
        "date", "dept_time", "arrv_time", "total_flight_time", "pft_pic",
        mode="after",
    )
    @classmethod
    def ensure_required_nonempty(cls, v):
        if v is None:
            raise ValueError("field is required")
        return v