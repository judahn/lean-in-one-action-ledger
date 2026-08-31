"""The One Action Update, assembled from a Circle's recent meetings. Pure: no I/O.

Read top to bottom in the order the moderator reads the page: what to raise,
then how the Circle is doing, then the line to open with.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.domain.model import Action, ActionStatus, Circle, Meeting, Member


@dataclass(frozen=True)
class MeetingRef:
    id: UUID
    held_at: datetime


@dataclass(frozen=True)
class CheckInAction:
    member: Member
    text: str
    status: ActionStatus
    note: str | None
    committed_at: MeetingRef
    carried_over: bool


@dataclass(frozen=True)
class FollowThrough:
    window_meetings: int
    committed: int
    done: int
    partly: int
    not_yet: int
    open: int
    rate: float | None


@dataclass(frozen=True)
class CheckIn:
    circle: Circle
    next_meeting: Meeting
    since_meeting: MeetingRef | None
    actions: list[CheckInAction]
    upcoming: list[CheckInAction]
    follow_through: FollowThrough
    opener: str


class CheckInAssembler:
    def assemble(self, circle: Circle, next_meeting: Meeting, past: list[Meeting]) -> CheckIn:
        """`past` is the window: the last N meetings, newest first.

        Every meeting arrives with its actions, the next one included.
        """
        since = past[0] if past else None
        listed = self._listed(circle, past)
        follow_through = self._follow_through(past)
        carried = sum(1 for a in listed if a.carried_over)
        return CheckIn(
            circle=circle,
            next_meeting=next_meeting,
            since_meeting=MeetingRef(since.id, since.held_at) if since else None,
            actions=listed,
            upcoming=self._upcoming(circle, next_meeting),
            follow_through=follow_through,
            opener=self._opener(follow_through, carried),
        )

    # Rule 1: carried-over first, oldest meeting first. Then this meeting's,
    # alphabetically. The tool remembers, it doesn't rank: grouping by status is
    # a switch on the page, the moderator's call.

    def _listed(self, circle: Circle, past: list[Meeting]) -> list[CheckInAction]:
        if not past:
            return []
        since, *earlier = past

        def name(action: Action) -> str:
            return circle.members[action.member_id].display_name

        carried = [
            self._entry(circle, m, a, carried_over=True)
            for m in sorted(earlier, key=lambda m: m.held_at)
            for a in sorted(m.actions, key=name)
            if a.status.is_open
        ]
        this_meeting = [
            self._entry(circle, since, a, carried_over=False)
            for a in sorted(since.actions, key=name)
        ]
        return carried + this_meeting

    def _entry(self, circle: Circle, m: Meeting, a: Action, carried_over: bool) -> CheckInAction:
        return CheckInAction(
            member=circle.members[a.member_id],
            text=a.text,
            status=a.status,
            note=a.note,
            committed_at=MeetingRef(m.id, m.held_at),
            carried_over=carried_over,
        )

    # Rule 2: rate over the window is (done + half of partly) / committed.
    # Partly counts as half on purpose: the ritual rewards movement, not perfection.
    # Nothing committed means no rate, not a bad month.

    def _follow_through(self, past: list[Meeting]) -> FollowThrough:
        counts = Counter(a.status for m in past for a in m.actions)
        committed = sum(counts.values())
        done, partly = counts[ActionStatus.done], counts[ActionStatus.partly]
        rate = round((done + 0.5 * partly) / committed, 2) if committed else None
        return FollowThrough(
            window_meetings=len(past),
            committed=committed,
            done=done,
            partly=partly,
            not_yet=counts[ActionStatus.not_yet],
            open=counts[ActionStatus.committed],
            rate=rate,
        )

    # Rule 3: the opener states the numbers and stops. Warmth is the moderator's,
    # or Claude's behind the flag.

    def _opener(self, ft: FollowThrough, carried: int) -> str:
        if ft.committed == 0:
            return "No One Actions on the ledger yet."
        span = (
            "at the last meeting"
            if ft.window_meetings == 1
            else f"over the last {ft.window_meetings} meetings"
        )
        line = f"{ft.done} of {_count(ft.committed, 'action')} landed {span}."
        if carried:
            line += (
                f" {carried} {'is' if carried == 1 else 'are'} carried over from earlier meetings."
            )
        return line

    # Rule 4: the upcoming group is what the Circle commits to before it leaves,
    # alphabetical like everything else. An entry can already carry a status,
    # because a member may report before the meeting.

    def _upcoming(self, circle: Circle, next_meeting: Meeting) -> list[CheckInAction]:
        def name(action: Action) -> str:
            return circle.members[action.member_id].display_name

        return [
            self._entry(circle, next_meeting, a, carried_over=False)
            for a in sorted(next_meeting.actions, key=name)
        ]


def _count(n: int, noun: str) -> str:
    return f"{n} {noun}{'' if n == 1 else 's'}"
