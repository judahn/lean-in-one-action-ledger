"""Meetings in Postgres, loaded with their actions."""

from datetime import datetime
from uuid import UUID

import psycopg

from app.domain.model import Meeting
from app.infrastructure.postgres.actions import ACTION_SELECT, action_from_row

MEETING_SELECT = "select id, circle_id, held_at, moderator_member_id from meetings "


def meeting_from_row(row: dict) -> Meeting:
    return Meeting(
        id=row["id"],
        circle_id=row["circle_id"],
        held_at=row["held_at"],
        moderator_member_id=row["moderator_member_id"],
    )


class PostgresMeetingRepository:
    def __init__(self, conn: psycopg.Connection):
        self.conn = conn

    def get(self, meeting_id: UUID) -> Meeting | None:
        row = self.conn.execute(MEETING_SELECT + "where id = %s", (meeting_id,)).fetchone()
        if row is None:
            return None
        return self._with_actions([meeting_from_row(row)])[0]

    def next_for(self, circle_id: UUID, after: datetime) -> Meeting | None:
        row = self.conn.execute(
            MEETING_SELECT + "where circle_id = %s and held_at > %s order by held_at asc limit 1",
            (circle_id, after),
        ).fetchone()
        if row is None:
            return None
        return self._with_actions([meeting_from_row(row)])[0]

    def recent_for(self, circle_id: UUID, before: datetime, limit: int) -> list[Meeting]:
        rows = self.conn.execute(
            MEETING_SELECT
            + "where circle_id = %s and held_at <= %s order by held_at desc limit %s",
            (circle_id, before, limit),
        ).fetchall()
        return self._with_actions([meeting_from_row(r) for r in rows])

    def _with_actions(self, meetings: list[Meeting]) -> list[Meeting]:
        """One query for all the meetings' actions, on the (circle_id, meeting_id) index."""
        if not meetings:
            return meetings
        by_id = {m.id: m for m in meetings}
        rows = self.conn.execute(
            ACTION_SELECT
            + "where a.circle_id = %s and a.meeting_id = any(%s) order by a.created_at",
            (meetings[0].circle_id, list(by_id)),
        ).fetchall()
        for row in rows:
            by_id[row["meeting_id"]].actions.append(action_from_row(row))
        return meetings
