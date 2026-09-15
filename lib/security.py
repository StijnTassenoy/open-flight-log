# Python Imports #
import secrets
import time
from collections import defaultdict

# External Imports #
from fastapi import Form, Request
from fastapi.exceptions import HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request as StarletteRequest
from starlette.responses import Response, PlainTextResponse
from starlette.status import (
    HTTP_403_FORBIDDEN,
    HTTP_429_TOO_MANY_REQUESTS,
)

RATE_LIMIT_REQUESTS = 60
RATE_LIMIT_WINDOW_SECONDS = 60

CSRF_COOKIE_NAME = "ofl_csrf"
CSRF_FIELD_NAME = "csrf_token"

# Endpoints that mutate state and therefore require CSRF + rate limiting.
_MUTATING_METHODS = {"POST", "PUT", "PATCH", "DELETE"}

_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "no-referrer",
    "X-XSS-Protection": "0",
    "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
    "Content-Security-Policy": (
        "default-src 'self'; "
        "script-src 'self'; "
        "style-src 'self'; "
        "img-src 'self' data:; "
        "font-src 'self'; "
        "connect-src 'self'; "
        "base-uri 'self'; "
        "form-action 'self'"
    ),
}


def _get_or_create_token(request: Request) -> str:
    token = request.cookies.get(CSRF_COOKIE_NAME)
    if not token:
        token = secrets.token_urlsafe(32)
    request.state.csrf_token = token
    return token


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: StarletteRequest, call_next):
        response = await call_next(request)
        for header, value in _HEADERS.items():
            response.headers.setdefault(header, value)
        return response


class CSRFTokenMiddleware(BaseHTTPMiddleware):
    """ Ensures a CSRF token cookie exists and exposes it via request.state. """

    async def dispatch(self, request: StarletteRequest, call_next):
        if request.method in _MUTATING_METHODS:
            return await call_next(request)

        token = _get_or_create_token(request)
        response = await call_next(request)
        if request.cookies.get(CSRF_COOKIE_NAME) is None:
            response.set_cookie(
                CSRF_COOKIE_NAME,
                token,
                httponly=True,
                samesite="lax",
                secure=False,
            )
        return response


async def validate_csrf(request: Request, csrf_token: str = Form(...)):
    """ Dependency-style CSRF validation (double-submit cookie). """
    cookie_token = request.cookies.get(CSRF_COOKIE_NAME)
    if not cookie_token or not csrf_token or not secrets.compare_digest(
        cookie_token, csrf_token
    ):
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="CSRF validation failed."
        )
    return csrf_token


class RateLimitMiddleware(BaseHTTPMiddleware):
    """ Simple per-IP sliding-window rate limiter for mutating endpoints. """

    def __init__(self, app, max_requests: int = RATE_LIMIT_REQUESTS,
                 window_seconds: int = RATE_LIMIT_WINDOW_SECONDS):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._hits: dict[str, list[float]] = defaultdict(list)

    async def dispatch(self, request: StarletteRequest, call_next):
        if request.method in _MUTATING_METHODS:
            client_ip = request.client.host if request.client else "unknown"
            now = time.time()
            window_start = now - self.window_seconds
            hits = [t for t in self._hits[client_ip] if t > window_start]

            if len(hits) >= self.max_requests:
                self._hits[client_ip] = hits
                return PlainTextResponse(
                    "Too many requests. Please try again later.",
                    status_code=HTTP_429_TOO_MANY_REQUESTS,
                )

            hits.append(now)
            self._hits[client_ip] = hits

        return await call_next(request)