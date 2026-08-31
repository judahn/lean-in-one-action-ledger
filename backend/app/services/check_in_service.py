"""Assemble the One Action Update for a Circle's next meeting."""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

from app.domain.check_in import CheckIn, CheckInAssembler
from app.domain.repositories import CircleRepository, MeetingRepository
from app.services.errors import Forbidden, NotFound


@dataclass
class CheckInService:
    circles: CircleRepository
    meetings: MeetingRepository
    assembler: CheckInAssembler = field(default_factory=CheckInAssembler)

    def assemble(
        self, circle_id: UUID, asking_member_id: UUID, window: int, as_of: datetime
    ) -> CheckIn:
        circle = self.circles.get(circle_id)
        if circle is None:
            raise NotFound("no such Circle")
        if not circle.has_member(asking_member_id):
            raise Forbidden("only members of the Circle can read its One Action Update")
        next_meeting = self.meetings.next_for(circle_id, after=as_of)
        if next_meeting is None:
            raise NotFound("no upcoming meeting is scheduled for this Circle")
        past = self.meetings.recent_for(circle_id, before=as_of, limit=window)
        return self.assembler.assemble(circle, next_meeting, past)
