"""A throwaway database on the compose Postgres, rebuilt once per session and reseeded per test."""

import os
from pathlib import Path
from uuid import UUID

import psycopg
import pytest
from psycopg.rows import dict_row

ROOT = Path(__file__).resolve().parents[2]
TEST_URL = os.environ.get(
    "TEST_DATABASE_URL", "postgresql://ledger:ledger@localhost:5433/ledger_test"
)
ADMIN_URL = TEST_URL.rsplit("/", 1)[0] + "/ledger"
TEST_DB = TEST_URL.rsplit("/", 1)[1]

# The app reads DATABASE_URL at request time, so point it at the test database
# before anything imports the app.
os.environ["DATABASE_URL"] = TEST_URL
os.environ["OPENER_AI"] = "0"

# Ids from db/seed.sql
CIRCLE = UUID("c0000000-0000-4000-8000-000000000001")
PRIYA = UUID("a0000000-0000-4000-8000-000000000001")
LENA = UUID("a0000000-0000-4000-8000-000000000002")
DANA = UUID("a0000000-0000-4000-8000-000000000003")
YUKI = UUID("a0000000-0000-4000-8000-000000000006")
MEETING_JULY = UUID("e0000000-0000-4000-8000-000000000002")
MEETING_AUG = UUID("e0000000-0000-4000-8000-000000000003")
MEETING_SEPT = UUID("e0000000-0000-4000-8000-000000000004")
ACTION_PRIYA_AUG = UUID("f0000000-0000-4000-8000-000000000801")
ACTION_LENA_JULY = UUID("f0000000-0000-4000-8000-000000000702")
ACTION_YUKI_AUG = UUID("f0000000-0000-4000-8000-000000000806")


@pytest.fixture(scope="session")
def test_database():
    with psycopg.connect(ADMIN_URL, autocommit=True) as admin:
        admin.execute(f"drop database if exists {TEST_DB}")
        admin.execute(f"create database {TEST_DB}")
    with psycopg.connect(TEST_URL, autocommit=True) as conn:
        conn.execute((ROOT / "db" / "schema.sql").read_text())
    yield TEST_URL


@pytest.fixture
def db(test_database):
    """A connection to a freshly seeded test database."""
    with psycopg.connect(test_database, autocommit=True, row_factory=dict_row) as conn:
        conn.execute("truncate circles, members restart identity cascade")
        conn.execute((ROOT / "db" / "seed.sql").read_text())
        yield conn


@pytest.fixture
def client(db):
    from fastapi.testclient import TestClient

    from app.api.main import app

    return TestClient(app)
