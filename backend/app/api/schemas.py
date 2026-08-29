"""Request and response shapes. The domain decides, these only carry."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.domain.check_in import CheckIn
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


class MemberOut(BaseModel):
    id: UUID
    display_name: str


class CircleOut(BaseModel):
    id: UUID
    name: str


class MeetingRefOut(BaseModel):
    id: UUID
    held_at: datetime


class NextMeetingOut(MeetingRefOut):
    moderator: MemberOut | None


class CheckInActionOut(BaseModel):
    member: MemberOut
    text: str
    status: ActionStatus
    note: str | None
    committed_at: MeetingRefOut
    carried_over: bool


class FollowThroughOut(BaseModel):
    window_meetings: int
    committed: int
    done: int
    partly: int
    not_yet: int
    open: int
    rate: float | None


class CheckInResponse(BaseModel):
    circle: CircleOut
    next_meeting: NextMeetingOut
    since_meeting: MeetingRefOut | None
    actions: list[CheckInActionOut]
    follow_through: FollowThroughOut
    opener: str
    opener_source: str

    @classmethod
    def from_domain(cls, c: CheckIn) -> "CheckInResponse":
        moderator = c.circle.members.get(c.next_meeting.moderator_member_id)
        return cls(
            circle=CircleOut(id=c.circle.id, name=c.circle.name),
            next_meeting=NextMeetingOut(
                id=c.next_meeting.id,
                held_at=c.next_meeting.held_at,
                moderator=MemberOut(**moderator.__dict__) if moderator else None,
            ),
            since_meeting=MeetingRefOut(**c.since_meeting.__dict__) if c.since_meeting else None,
            actions=[
                CheckInActionOut(
                    member=MemberOut(**a.member.__dict__),
                    text=a.text,
                    status=a.status,
                    note=a.note,
                    committed_at=MeetingRefOut(**a.committed_at.__dict__),
                    carried_over=a.carried_over,
                )
                for a in c.actions
            ],
            follow_through=FollowThroughOut(**c.follow_through.__dict__),
            opener=c.opener,
            opener_source=c.opener_source,
        )
