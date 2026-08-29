"""The optional AI opener. Off unless OPENER_AI=1. The template is always the fallback.

The facts sent to Claude are the same ones the room hears read aloud, nothing more.
"""

import logging
import os
from dataclasses import replace
from pathlib import Path

import anthropic

from app.domain.check_in import CheckIn

PROMPT = Path(__file__).with_name("opener_prompt.md")
log = logging.getLogger(__name__)


def ai_opener_enabled() -> bool:
    return os.environ.get("OPENER_AI", "0") == "1"


def facts_for(check_in: CheckIn) -> str:
    ft = check_in.follow_through
    lines = [
        f"Circle: {check_in.circle.name}",
        f"Next meeting: {check_in.next_meeting.held_at:%B %-d}",
        f"Window: last {ft.window_meetings} meetings",
        f"Committed {ft.committed}, done {ft.done}, partly {ft.partly}, "
        f"not yet {ft.not_yet}, not reported {ft.open}",
        "Actions:",
    ]
    for a in check_in.actions:
        carried = " (carried over)" if a.carried_over else ""
        note = f' "{a.note}"' if a.note else ""
        lines.append(f"- {a.member.display_name}: {a.text} [{a.status}]{carried}{note}")
    return "\n".join(lines)


class ClaudeOpener:
    def __init__(self, model: str | None = None):
        self.model = model or os.environ.get("OPENER_MODEL", "claude-opus-5")

    def rewrite(self, check_in: CheckIn) -> CheckIn:
        try:
            response = anthropic.Anthropic().beta.messages.create(
                model=self.model,
                max_tokens=256,
                betas=["server-side-fallback-2026-07-01"],
                fallbacks="default",
                output_config={"effort": "low"},
                system=PROMPT.read_text(),
                messages=[{"role": "user", "content": facts_for(check_in)}],
            )
        except (
            anthropic.APIStatusError,
            anthropic.APIConnectionError,
            anthropic.AnthropicError,
        ) as e:
            log.warning("opener: Claude unavailable, keeping the template (%s)", e)
            return check_in
        if response.stop_reason == "refusal":
            return check_in
        text = "".join(b.text for b in response.content if b.type == "text").strip()
        return replace(check_in, opener=text, opener_source="claude") if text else check_in
