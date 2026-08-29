"""Circles in Postgres, loaded with their members."""

from uuid import UUID

import psycopg

from app.domain.model import Circle, Member


class PostgresCircleRepository:
    def __init__(self, conn: psycopg.Connection):
        self.conn = conn

    def get(self, circle_id: UUID) -> Circle | None:
        row = self.conn.execute(
            "select id, name from circles where id = %s", (circle_id,)
        ).fetchone()
        if row is None:
            return None
        members = self.conn.execute(
            """
            select m.id, m.display_name
              from members m
              join memberships ms on ms.member_id = m.id
             where ms.circle_id = %s
            """,
            (circle_id,),
        ).fetchall()
        return Circle(
            id=row["id"],
            name=row["name"],
            members={m["id"]: Member(id=m["id"], display_name=m["display_name"]) for m in members},
        )
