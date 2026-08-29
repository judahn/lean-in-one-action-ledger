"""Request and response shapes. The domain decides, these only carry."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.domain.model import Action, ActionStatus


class RecordActionRequest(BaseModel):
    text: str = Field(min_length=1)
    why: str | None = None


class ReportActionRequest(BaseModel):
    status: ActionStatus
    note: str | None = None


class ActionResponse(BaseModel):
    id: UUID
    meeting_id: UUID
    member_id: UUID
    circle_id: UUID
    text: str
    why: str | None
    status: ActionStatus
    note: str | None
    created_at: datetime | None

    @classmethod
    def from_domain(cls, action: Action) -> "ActionResponse":
        return cls(**action.__dict__)
