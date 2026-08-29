"""CheckInAssembler, rule by rule, from the spec's example response. No database."""

from datetime import datetime, timezone
from uuid import uuid4

import pytest

from app.domain.check_in import CheckInAssembler
from app.domain.model import Action, ActionStatus, Circle, Meeting, Member

C = ActionStatus.committed
D = ActionStatus.done
P = ActionStatus.partly
N = ActionStatus.not_yet


def at(month: int, day: int) -> datetime:
    return datetime(2026, month, day, 18, 0, tzinfo=timezone.utc)


@pytest.fixture
def circle() -> Circle:
    names = ["Priya", "Lena", "Dana", "Grace", "Yuki"]
    members = {uuid4(): Member(id=None, display_name=n) for n in names}
    members = {mid: Member(id=mid, display_name=m.display_name) for mid, m in members.items()}
    return Circle(id=uuid4(), name="West Coast Execs", members=members)


def meeting(circle: Circle, held_at: datetime, statuses: dict[str, ActionStatus]) -> Meeting:
    """A past meeting with one action per named member, in the given status."""
    m = Meeting(id=uuid4(), circle_id=circle.id, held_at=held_at)
    by_name = {member.display_name: member for member in circle.members.values()}
    for name, status in statuses.items():
        m.actions.append(
            Action(
                id=uuid4(),
                meeting_id=m.id,
                member_id=by_name[name].id,
                circle_id=circle.id,
                text=f"{name}'s action from {held_at:%B}",
                status=status,
            )
        )
    return m


@pytest.fixture
def past(circle: Circle) -> list[Meeting]:
    """Newest first, as the repository returns them. 15 actions over three meetings."""
    june = meeting(circle, at(6, 11), {"Priya": D, "Lena": N, "Dana": D, "Grace": D, "Yuki": N})
    july = meeting(circle, at(7, 9), {"Priya": D, "Lena": C, "Dana": P, "Grace": D, "Yuki": D})
    aug = meeting(circle, at(8, 13), {"Priya": D, "Grace": D, "Dana": P, "Yuki": N, "Lena": C})
    return [aug, july, june]


@pytest.fixture
def next_meeting(circle: Circle) -> Meeting:
    return Meeting(id=uuid4(), circle_id=circle.id, held_at=at(9, 10))


def names(check_in) -> list[str]:
    return [a.member.display_name for a in check_in.actions]


# Rule 1: what gets listed, and in what order


def test_carried_over_actions_come_first_oldest_first(circle, next_meeting, past):
    check_in = CheckInAssembler().assemble(circle, next_meeting, past)

    carried = [a for a in check_in.actions if a.carried_over]
    assert check_in.actions[:3] == carried
    assert [a.committed_at.held_at for a in carried] == [at(6, 11), at(6, 11), at(7, 9)]
    assert [a.status for a in carried] == [N, N, C]


def test_carried_over_from_the_same_meeting_read_alphabetically(circle, next_meeting, past):
    check_in = CheckInAssembler().assemble(circle, next_meeting, past)

    assert names(check_in)[:2] == ["Lena", "Yuki"]


def test_this_meetings_actions_read_alphabetically_whatever_their_status(
    circle, next_meeting, past
):
    check_in = CheckInAssembler().assemble(circle, next_meeting, past)

    this_meeting = [a for a in check_in.actions if not a.carried_over]
    assert [a.member.display_name for a in this_meeting] == [
        "Dana",
        "Grace",
        "Lena",
        "Priya",
        "Yuki",
    ]
    assert [a.status for a in this_meeting] == [P, D, C, D, N]
    assert all(a.committed_at.held_at == at(8, 13) for a in this_meeting)


def test_finished_actions_from_older_meetings_are_not_listed(circle, next_meeting, past):
    check_in = CheckInAssembler().assemble(circle, next_meeting, past)

    older = [a for a in check_in.actions if a.committed_at.held_at < at(8, 13)]
    assert all(a.status.is_open for a in older)


def test_since_meeting_is_the_most_recent_past_one(circle, next_meeting, past):
    check_in = CheckInAssembler().assemble(circle, next_meeting, past)

    assert check_in.since_meeting.held_at == at(8, 13)
    assert check_in.next_meeting.held_at == at(9, 10)


# Rule 2: follow-through over the window


def test_follow_through_counts_the_window_and_halves_partly(circle, next_meeting, past):
    check_in = CheckInAssembler().assemble(circle, next_meeting, past)

    ft = check_in.follow_through
    assert (ft.window_meetings, ft.committed) == (3, 15)
    assert (ft.done, ft.partly, ft.not_yet, ft.open) == (8, 2, 3, 2)
    assert ft.rate == round((8 + 0.5 * 2) / 15, 2)


def test_follow_through_rate_is_null_with_nothing_committed(circle, next_meeting):
    quiet_meeting = Meeting(id=uuid4(), circle_id=circle.id, held_at=at(8, 13))

    check_in = CheckInAssembler().assemble(circle, next_meeting, [quiet_meeting])

    assert check_in.follow_through.committed == 0
    assert check_in.follow_through.rate is None


def test_a_circle_with_no_past_meetings_gets_an_empty_check_in(circle, next_meeting):
    check_in = CheckInAssembler().assemble(circle, next_meeting, [])

    assert check_in.since_meeting is None
    assert check_in.actions == []
    assert check_in.follow_through.rate is None


# Rule 3: the opener states the numbers and stops


def test_the_opener_states_the_numbers(circle, next_meeting, past):
    check_in = CheckInAssembler().assemble(circle, next_meeting, past)

    assert check_in.opener == (
        "8 of 15 actions landed over the last 3 meetings. 3 are carried over from earlier meetings."
    )
    assert check_in.opener_source == "template"


def test_the_opener_skips_carry_over_when_there_is_none(circle, next_meeting, past):
    check_in = CheckInAssembler().assemble(circle, next_meeting, past[:1])

    assert check_in.opener == "2 of 5 actions landed at the last meeting."


def test_the_opener_for_an_empty_ledger(circle, next_meeting):
    check_in = CheckInAssembler().assemble(circle, next_meeting, [])

    assert check_in.opener == "No One Actions on the ledger yet."
