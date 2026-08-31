"""The One Action Ledger API. Domain and service errors map to HTTP here and nowhere else."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.routers import actions, check_in
from app.domain.errors import (
    ActionAlreadyReported,
    DuplicateAction,
    InvalidStatusTransition,
    MeetingNotInCircle,
    NotAMember,
)
from app.services.errors import Forbidden, NotFound

app = FastAPI(title="One Action Ledger", version="0.1.0")
app.include_router(actions.router)
app.include_router(check_in.router)

STATUS_FOR = {
    DuplicateAction: 409,
    NotAMember: 403,
    Forbidden: 403,
    InvalidStatusTransition: 422,
    ActionAlreadyReported: 422,
    MeetingNotInCircle: 404,
    NotFound: 404,
}


def _as_http(status: int):
    def handler(_: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(status_code=status, content={"detail": str(exc)})

    return handler


for error, status in STATUS_FOR.items():
    app.add_exception_handler(error, _as_http(status))
