"""The One Action Update for the next meeting. The endpoint that does real work."""

from datetime import datetime, timezone
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Query

from app.api.deps import AskingMember, CheckIns
from app.api.schemas import CheckInResponse

router = APIRouter(tags=["check-in"])


@router.get("/circles/{circle_id}/meetings/next/check-in")
def next_check_in(
    circle_id: UUID,
    member: AskingMember,
    check_ins: CheckIns,
    window: Annotated[int, Query(ge=1, le=12)] = 3,
    as_of: datetime | None = None,
) -> CheckInResponse:
    """`as_of` fixes the clock for demos and tests. Defaults to now."""
    now = as_of or datetime.now(timezone.utc)
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    return CheckInResponse.from_domain(check_ins.assemble(circle_id, member, window, now))
