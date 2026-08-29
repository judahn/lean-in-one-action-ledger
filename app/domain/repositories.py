"""Repository interfaces. The domain owns the shape, infrastructure fills it."""

from __future__ import annotations

from datetime import datetime
from typing import Protocol
from uuid import UUID

from app.domain.model import Action, ActionUpdate, Circle, Meeting


class CircleRepository(Protocol):
    def get(self, circle_id: UUID) -> Circle | None:
        """The Circle with its members loaded."""
        ...


class MeetingRepository(Protocol):
    def get(self, meeting_id: UUID) -> Meeting | None:
        """A meeting with its actions loaded."""
        ...

    def next_for(self, circle_id: UUID, after: datetime) -> Meeting | None:
        """The first meeting of the Circle held after the given moment."""
        ...

    def recent_for(self, circle_id: UUID, before: datetime, limit: int) -> list[Meeting]:
        """The last `limit` meetings held at or before the moment, newest first, with actions."""
        ...


class ActionRepository(Protocol):
    def get(self, action_id: UUID) -> Action | None: ...

    def add(self, action: Action) -> Action:
        """Persist a new action. Returns it with created_at set."""
        ...

    def report(self, action: Action, update: ActionUpdate) -> None:
        """Append the update and set the action's current status."""
        ...

    def list_for_member(self, member_id: UUID) -> list[Action]:
        """A member's own history, newest first."""
        ...
