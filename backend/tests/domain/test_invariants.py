"""The three aggregate rules from the spec. No database."""

from datetime import datetime, timezone
from uuid import uuid4

import pytest

from app.domain.errors import (
    DuplicateAction,
    InvalidStatusTransition,
    MeetingNotInCircle,
    NotAMember,
)
from app.domain.model import ActionStatus, Circle, Meeting, Member

AUG = datetime(2026, 8, 13, 18, 0, tzinfo=timezone.utc)


def circle_with(*members: Member) -> Circle:
    return Circle(id=uuid4(), name="West Coast Execs", members={m.id: m for m in members})


def meeting_of(circle: Circle) -> Meeting:
    return Meeting(id=uuid4(), circle_id=circle.id, held_at=AUG)


# Invariant 1: one action per member per meeting


def test_a_member_records_one_action_per_meeting():
    priya = Member(id=uuid4(), display_name="Priya")
    circle = circle_with(priya)
    meeting = meeting_of(circle)

    circle.record_action(meeting, priya.id, "Ask Marcus for the Q4 launch to lead")

    with pytest.raises(DuplicateAction):
        circle.record_action(meeting, priya.id, "A second one")


# Invariant 2: the action's member belongs to the action's Circle


def test_an_action_needs_a_member_of_the_circle():
    priya = Member(id=uuid4(), display_name="Priya")
    circle = circle_with(priya)
    meeting = meeting_of(circle)
    stranger = uuid4()

    with pytest.raises(NotAMember):
        circle.record_action(meeting, stranger, "Book the informational")


def test_an_action_needs_a_meeting_of_this_circle():
    priya = Member(id=uuid4(), display_name="Priya")
    circle = circle_with(priya)
    other_circles_meeting = Meeting(id=uuid4(), circle_id=uuid4(), held_at=AUG)

    with pytest.raises(MeetingNotInCircle):
        circle.record_action(other_circles_meeting, priya.id, "Book the informational")


# Invariant 3: status only moves forward from committed


def test_a_report_moves_a_committed_action_forward():
    priya = Member(id=uuid4(), display_name="Priya")
    circle = circle_with(priya)
    action = circle.record_action(meeting_of(circle), priya.id, "Ask Marcus")

    action.report(ActionStatus.done, note="Asked Tuesday. He said yes.")

    assert action.status is ActionStatus.done
    assert action.note == "Asked Tuesday. He said yes."


def test_a_report_can_revise_among_done_partly_and_not_yet():
    priya = Member(id=uuid4(), display_name="Priya")
    circle = circle_with(priya)
    action = circle.record_action(meeting_of(circle), priya.id, "Ask Marcus")

    action.report(ActionStatus.partly)
    action.report(ActionStatus.done)

    assert action.status is ActionStatus.done


def test_an_action_never_returns_to_committed():
    priya = Member(id=uuid4(), display_name="Priya")
    circle = circle_with(priya)
    action = circle.record_action(meeting_of(circle), priya.id, "Ask Marcus")
    action.report(ActionStatus.partly)

    with pytest.raises(InvalidStatusTransition):
        action.report(ActionStatus.committed)
