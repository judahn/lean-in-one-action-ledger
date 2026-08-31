"""One test per endpoint, plus the privacy rules at the edge (they are requirements)."""

from uuid import uuid4

from tests.conftest import (
    ACTION_PRIYA_AUG,
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


def test_a_member_rewords_her_own_action_until_she_reports(client):
    response = client.patch(
        f"/actions/{ACTION_YUKI_AUG}",
        json={"text": "Re-raise the title change with Elena", "why": "She owns the ladder"},
        headers=as_member(YUKI),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["text"] == "Re-raise the title change with Elena"
    assert body["why"] == "She owns the ladder"
    assert body["status"] == "committed"


def test_a_reported_action_keeps_the_wording_the_circle_heard(client):
    response = client.patch(
        f"/actions/{ACTION_PRIYA_AUG}",
        json={"text": "Something easier", "why": None},
        headers=as_member(PRIYA),
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


# GET /circles/{circle_id}/meetings/next/check-in

AS_OF = "2026-08-29T12:00:00Z"


def test_the_check_in_has_the_example_shape(client):
    response = client.get(
        f"/circles/{CIRCLE}/meetings/next/check-in",
        params={"as_of": AS_OF},
        headers=as_member(PRIYA),
    )

    assert response.status_code == 200
    body = response.json()
    assert set(body) == {
        "circle",
        "next_meeting",
        "since_meeting",
        "actions",
        "upcoming",
        "follow_through",
        "opener",
        "opener_source",
    }
    assert body["circle"]["name"] == "West Coast Execs"
    assert body["next_meeting"]["moderator"]["display_name"] == "Dana"
    assert body["since_meeting"]["id"] == str(MEETING_AUG)
    assert set(body["actions"][0]) == {
        "member",
        "text",
        "status",
        "note",
        "committed_at",
        "carried_over",
    }
    carried = [a["member"]["display_name"] for a in body["actions"] if a["carried_over"]]
    assert carried == ["Yuki", "Lena"]
    assert set(body["upcoming"][0]) == {
        "member",
        "text",
        "status",
        "note",
        "committed_at",
        "carried_over",
    }
    assert [a["member"]["display_name"] for a in body["upcoming"]] == ["Grace", "Yuki"]
    assert body["upcoming"][0]["committed_at"]["id"] == body["next_meeting"]["id"]
    assert body["follow_through"] == {
        "window_meetings": 3,
        "committed": 24,
        "done": 15,
        "partly": 4,
        "not_yet": 3,
        "open": 2,
        "rate": 0.71,
    }
    assert body["opener_source"] == "template"


def test_a_non_member_cannot_read_the_check_in(client):
    response = client.get(
        f"/circles/{CIRCLE}/meetings/next/check-in",
        params={"as_of": AS_OF},
        headers=as_member(uuid4()),
    )

    assert response.status_code == 403
