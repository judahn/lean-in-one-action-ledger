"""One test per endpoint, plus the privacy rules at the edge (they are requirements)."""

from uuid import uuid4

from tests.conftest import (
    ACTION_YUKI_AUG,
    CIRCLE,
    LENA,
    MEETING_AUG,
    MEETING_SEPT,
    PRIYA,
    YUKI,
)


def as_member(member_id) -> dict:
    return {"X-Member-Id": str(member_id)}


# POST /circles/{circle_id}/meetings/{meeting_id}/actions


def test_a_member_records_an_action_for_a_meeting(client):
    response = client.post(
        f"/circles/{CIRCLE}/meetings/{MEETING_SEPT}/actions",
        json={"text": "Ask for the platform org", "why": "It is the job I want"},
        headers=as_member(PRIYA),
    )

    assert response.status_code == 201
    body = response.json()
    assert body["text"] == "Ask for the platform org"
    assert body["status"] == "committed"
    assert body["member_id"] == str(PRIYA)


def test_a_second_action_in_the_same_meeting_is_refused(client):
    response = client.post(
        f"/circles/{CIRCLE}/meetings/{MEETING_AUG}/actions",
        json={"text": "A second one", "why": None},
        headers=as_member(PRIYA),
    )

    assert response.status_code == 409


def test_a_non_member_cannot_record_an_action(client):
    response = client.post(
        f"/circles/{CIRCLE}/meetings/{MEETING_SEPT}/actions",
        json={"text": "Sneaking in", "why": None},
        headers=as_member(uuid4()),
    )

    assert response.status_code == 403


# PATCH /actions/{action_id}


def test_a_member_reports_on_her_own_action(client):
    response = client.patch(
        f"/actions/{ACTION_YUKI_AUG}",
        json={"status": "done", "note": "Raised it Monday. Title lands in October."},
        headers=as_member(YUKI),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "done"
    assert body["note"] == "Raised it Monday. Title lands in October."


def test_only_the_actions_own_member_may_report_on_it(client):
    response = client.patch(
        f"/actions/{ACTION_YUKI_AUG}",
        json={"status": "done", "note": None},
        headers=as_member(PRIYA),
    )

    assert response.status_code == 403


def test_a_report_back_to_committed_is_refused(client):
    response = client.patch(
        f"/actions/{ACTION_YUKI_AUG}",
        json={"status": "committed", "note": None},
        headers=as_member(YUKI),
    )

    assert response.status_code == 422


# GET /members/{member_id}/actions


def test_a_member_reads_her_own_history_newest_first(client):
    response = client.get(f"/members/{PRIYA}/actions", headers=as_member(PRIYA))

    assert response.status_code == 200
    texts = [a["text"] for a in response.json()]
    assert texts == [
        "Ask Marcus for the Q4 launch to lead",
        "Ask Marcus to co-present at the all-hands",
        "Send the promo case to my skip-level",
    ]


def test_a_member_cannot_read_another_members_history(client):
    response = client.get(f"/members/{PRIYA}/actions", headers=as_member(LENA))

    assert response.status_code == 403
