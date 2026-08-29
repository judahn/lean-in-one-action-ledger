"""Record a One Action, report on it, read your own history."""

from uuid import UUID

from fastapi import APIRouter

from app.api.deps import Actions, AskingMember
from app.api.schemas import ActionResponse, RecordActionRequest, ReportActionRequest

router = APIRouter(tags=["actions"])


@router.post("/circles/{circle_id}/meetings/{meeting_id}/actions", status_code=201)
def record_action(
    circle_id: UUID,
    meeting_id: UUID,
    body: RecordActionRequest,
    member: AskingMember,
    actions: Actions,
) -> ActionResponse:
    action = actions.record(circle_id, meeting_id, member, body.text, body.why)
    return ActionResponse.from_domain(action)


@router.patch("/actions/{action_id}")
def report_action(
    action_id: UUID, body: ReportActionRequest, member: AskingMember, actions: Actions
) -> ActionResponse:
    action = actions.report(action_id, member, body.status, body.note)
    return ActionResponse.from_domain(action)


@router.get("/members/{member_id}/actions")
def member_history(member_id: UUID, member: AskingMember, actions: Actions) -> list[ActionResponse]:
    return [ActionResponse.from_domain(a) for a in actions.history(member_id, member)]
