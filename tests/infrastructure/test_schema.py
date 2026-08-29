"""The schema refuses what the aggregate refuses. One test per backing constraint."""

import psycopg.errors
import pytest

from tests.conftest import ACTION_PRIYA_AUG, CIRCLE, MEETING_AUG, PRIYA


def test_the_database_refuses_a_second_action_for_a_member_in_a_meeting(db):
    with pytest.raises(psycopg.errors.UniqueViolation):
        db.execute(
            "insert into actions (meeting_id, member_id, circle_id, text) values (%s, %s, %s, %s)",
            (MEETING_AUG, PRIYA, CIRCLE, "A second one"),
        )


def test_the_database_refuses_an_update_back_to_committed(db):
    with pytest.raises(psycopg.errors.CheckViolation):
        db.execute(
            "insert into action_updates (action_id, status) values (%s, 'committed')",
            (ACTION_PRIYA_AUG,),
        )
