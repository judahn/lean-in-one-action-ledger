"""FastAPI dependencies: the request's connection, who is asking, and the services."""

from collections.abc import Iterator
from typing import Annotated
from uuid import UUID

import psycopg
from fastapi import Depends, Header

from app.infrastructure.db import transaction
from app.infrastructure.postgres.actions import PostgresActionRepository
from app.infrastructure.postgres.circles import PostgresCircleRepository
from app.infrastructure.postgres.meetings import PostgresMeetingRepository
from app.services.action_service import ActionService
from app.services.check_in_service import CheckInService


def connection() -> Iterator[psycopg.Connection]:
    with transaction() as conn:
        yield conn


def asking_member(x_member_id: Annotated[UUID, Header()]) -> UUID:
    """Identity is out of scope for the take-home. The header says who is asking."""
    return x_member_id


def action_service(conn: Annotated[psycopg.Connection, Depends(connection)]) -> ActionService:
    return ActionService(
        circles=PostgresCircleRepository(conn),
        meetings=PostgresMeetingRepository(conn),
        actions=PostgresActionRepository(conn),
    )


def check_in_service(conn: Annotated[psycopg.Connection, Depends(connection)]) -> CheckInService:
    return CheckInService(
        circles=PostgresCircleRepository(conn),
        meetings=PostgresMeetingRepository(conn),
    )


Connection = Annotated[psycopg.Connection, Depends(connection)]
AskingMember = Annotated[UUID, Depends(asking_member)]
Actions = Annotated[ActionService, Depends(action_service)]
CheckIns = Annotated[CheckInService, Depends(check_in_service)]
