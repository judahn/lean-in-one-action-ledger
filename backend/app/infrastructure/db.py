"""One connection per request, one transaction. Commits on success, rolls back on error."""

import os
from collections.abc import Iterator
from contextlib import contextmanager

import psycopg
from psycopg.rows import dict_row

DEFAULT_URL = "postgresql://ledger:ledger@localhost:5433/ledger"


def database_url() -> str:
    return os.environ.get("DATABASE_URL", DEFAULT_URL)


@contextmanager
def transaction() -> Iterator[psycopg.Connection]:
    with psycopg.connect(database_url(), row_factory=dict_row) as conn:
        yield conn
