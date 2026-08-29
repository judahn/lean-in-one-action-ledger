"""Record, report, and read back One Actions. Thin: loads, delegates to the domain, saves."""

from dataclasses import dataclass
from uuid import UUID

from app.domain.model import Action, ActionStatus
from app.domain.repositories import ActionRepository, CircleRepository, MeetingRepository
from app.services.errors import Forbidden, NotFound


@dataclass
class ActionService:
    circles: CircleRepository
    meetings: MeetingRepository
    actions: ActionRepository

    def record(
        self, circle_id: UUID, meeting_id: UUID, member_id: UUID, text: str, why: str | None
    ) -> Action:
        circle = self.circles.get(circle_id)
        if circle is None:
            raise NotFound("no such Circle")
        meeting = self.meetings.get(meeting_id)
        if meeting is None:
            raise NotFound("no such meeting")
        action = circle.record_action(meeting, member_id, text, why)
        return self.actions.add(action)

    def report(
        self, action_id: UUID, member_id: UUID, status: ActionStatus, note: str | None
    ) -> Action:
        action = self.actions.get(action_id)
        if action is None:
            raise NotFound("no such action")
        if action.member_id != member_id:
            raise Forbidden("only the action's own member may report on it")
        update = action.report(status, note)
        self.actions.report(action, update)
        return action

    def history(self, member_id: UUID, asking_member_id: UUID) -> list[Action]:
        if member_id != asking_member_id:
            raise Forbidden("a member sees only her own history")
        return self.actions.list_for_member(member_id)
