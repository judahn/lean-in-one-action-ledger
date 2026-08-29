"""Actions in Postgres. The latest update's note rides along as the action's current note."""

from uuid import UUID

import psycopg

from app.domain.model import Action, ActionStatus, ActionUpdate

ACTION_SELECT = """
select a.id, a.meeting_id, a.member_id, a.circle_id, a.text, a.why, a.status, a.created_at,
       (select u.note from action_updates u
         where u.action_id = a.id order by u.created_at desc limit 1) as note
  from actions a
"""


def action_from_row(row: dict) -> Action:
    return Action(
        id=row["id"],
        meeting_id=row["meeting_id"],
        member_id=row["member_id"],
        circle_id=row["circle_id"],
        text=row["text"],
        why=row["why"],
        status=ActionStatus(row["status"]),
        note=row["note"],
        created_at=row["created_at"],
    )


class PostgresActionRepository:
    def __init__(self, conn: psycopg.Connection):
        self.conn = conn

    def get(self, action_id: UUID) -> Action | None:
        row = self.conn.execute(ACTION_SELECT + "where a.id = %s", (action_id,)).fetchone()
        return action_from_row(row) if row else None

    def add(self, action: Action) -> Action:
        row = self.conn.execute(
            """
            insert into actions (id, meeting_id, member_id, circle_id, text, why, status)
            values (%s, %s, %s, %s, %s, %s, %s)
            returning created_at
            """,
            (
                action.id,
                action.meeting_id,
                action.member_id,
                action.circle_id,
                action.text,
                action.why,
                action.status.value,
            ),
        ).fetchone()
        action.created_at = row["created_at"]
        return action

    def report(self, action: Action, update: ActionUpdate) -> None:
        self.conn.execute(
            "insert into action_updates (action_id, status, note) values (%s, %s, %s)",
            (update.action_id, update.status.value, update.note),
        )
        self.conn.execute(
            "update actions set status = %s where id = %s", (update.status.value, action.id)
        )

    def list_for_member(self, member_id: UUID) -> list[Action]:
        rows = self.conn.execute(
            ACTION_SELECT + "where a.member_id = %s order by a.created_at desc", (member_id,)
        ).fetchall()
        return [action_from_row(r) for r in rows]
