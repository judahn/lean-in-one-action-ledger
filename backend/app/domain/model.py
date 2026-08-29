"""Entities and value objects of the Circle Commitments context.

Circle is the aggregate root and owns its Meetings. Meeting owns its Actions.
The three invariants from the spec are enforced here, not left to the schema.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from uuid import UUID, uuid4

from app.domain.errors import (
    DuplicateAction,
    InvalidStatusTransition,
    MeetingNotInCircle,
    NotAMember,
)


class ActionStatus(StrEnum):
    committed = "committed"
    done = "done"
    partly = "partly"
    not_yet = "not_yet"

    @property
    def is_open(self) -> bool:
        """Still needs the member's attention at the next meeting."""
        return self in (ActionStatus.committed, ActionStatus.not_yet)


@dataclass(frozen=True)
class Member:
    id: UUID
    display_name: str


@dataclass(frozen=True)
class ActionUpdate:
    """One report on an action. Appended, never edited."""

    action_id: UUID
    status: ActionStatus
    note: str | None = None


@dataclass
class Action:
    id: UUID
    meeting_id: UUID
    member_id: UUID
    circle_id: UUID
    text: str
    why: str | None = None
    status: ActionStatus = ActionStatus.committed
    note: str | None = None
    created_at: datetime | None = None

    def report(self, status: ActionStatus, note: str | None = None) -> ActionUpdate:
        """Invariant 3: forward from committed, revisable among the rest."""
        if status is ActionStatus.committed:
            raise InvalidStatusTransition("an action never returns to committed")
        self.status = status
        self.note = note
        return ActionUpdate(action_id=self.id, status=status, note=note)


@dataclass
class Meeting:
    id: UUID
    circle_id: UUID
    held_at: datetime
    moderator_member_id: UUID | None = None
    actions: list[Action] = field(default_factory=list)

    def record_action(self, member_id: UUID, text: str, why: str | None = None) -> Action:
        """Invariant 1: one action per member per meeting."""
        if any(a.member_id == member_id for a in self.actions):
            raise DuplicateAction("this member already has an action for this meeting")
        action = Action(
            id=uuid4(),
            meeting_id=self.id,
            member_id=member_id,
            circle_id=self.circle_id,
            text=text,
            why=why,
        )
        self.actions.append(action)
        return action


@dataclass
class Circle:
    id: UUID
    name: str
    members: dict[UUID, Member] = field(default_factory=dict)

    def has_member(self, member_id: UUID) -> bool:
        return member_id in self.members

    def record_action(
        self, meeting: Meeting, member_id: UUID, text: str, why: str | None = None
    ) -> Action:
        """Invariant 2 here, invariant 1 in the meeting."""
        if meeting.circle_id != self.id:
            raise MeetingNotInCircle("that meeting belongs to another Circle")
        if not self.has_member(member_id):
            raise NotAMember("only a member of the Circle can commit to an action")
        return meeting.record_action(member_id, text, why)
