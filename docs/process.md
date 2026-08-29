# How this was built

Spec first, in my words: the feature, the domain model, the invariants,
the privacy rules, what's out of scope. Claude Code built against that
spec, tests first. I read every file as it landed, ran the suite, and
paired on `CheckInAssembler` one rule at a time. `design.md` and this file
are mine.

## Choosing the feature

The brief offered three examples (Circle health, recommendations, a
research content API). Before picking, I wanted to know what Lean In's
platform is today and what a Circle is like from the inside. Claude Code
did the reading, I did the choosing.

- leanin.org and connect.leanin.org: the Circles directory (a flat list of
  free-text names, no filters), the Networks directory, and the Resources
  shelf, whose "Circle leader tips" titles read like a roadmap ("Staying
  connected between meetings," "How to reignite energy in your Circle,"
  "How do you know your Circle is working?").
- The Circle 1-2-3 Meeting Guide PDF, the ritual itself: Check-In,
  Activities, One Action, Wrap-Up, and the One Action Update worksheet that
  opens the next meeting.
- Member accounts in the press (Slate, BuzzFeed News, BUST): the curriculum
  felt rigid, the old scheduling tool was abandoned for email and Doodle,
  confidentiality is load-bearing, and Circles connect between meetings on
  email and Facebook groups rather than on the platform.
- Coverage of Lean In's 2026 AI gender gap research and the new CEO's
  direction, to see what the organization is pushing now.

Seven candidates came out of that, from the obvious (Circle matching, which
half the field will build) to the topical (an AI wins ledger tied to the
recognition gap). The One Action Ledger won because the One Action is
already Lean In's own ritual and the platform doesn't hold it: the
commitment lives on a printout and the follow-through happens on email.
Nothing new to teach a Circle. The runner-up, a Circle health snapshot,
builds on the same schema and is in `design.md` as what I'd do next.

## Decisions

- One Action Ledger over six other candidates, for the reason above.
- Postgres in Docker, plain `schema.sql`, psycopg, no ORM. The brief grades
  schema and indexing, and every query should be explainable.
- Light DDD: one bounded context, two aggregates, invariants enforced in
  the aggregate and backed by constraints in the schema. Services
  orchestrate directly, no use-case layer. Small enough to read in ten
  minutes.
- Identity out of scope: an `X-Member-Id` header, membership checked in
  the service, and a note in `design.md` on how real auth replaces it.
- AI in the product only where it's optional and visible: the moderator's
  opener, behind a flag, prompt in the repo, `opener_source` in the
  response.
- Privacy as requirements, not vibes: no per-member rates, no rankings.
- TDD, scoped to what would break if changed: the invariants, the
  assembler, the schema constraints, one test per endpoint. Tests drive the
  public surface and mock only at I/O.
- Modules split at about 200 lines, by responsibility.
- uv for the environment, my first project on it. Two commands for the
  reviewer, and I wanted the practice.
- The Update lists this meeting's actions alphabetically, with grouping by
  status as a switch on the page. I had first specified "done first." That
  was the tool ranking people, and I took it out.
- Counts first, the rate small, and no rate at all when nothing was
  committed. A Circle is not a scoreboard.
- An action recorded for the upcoming meeting is reportable right away and
  shows in your own rail, with a line on when it reads out. The wall reads
  the previous meeting's commitments only.
- The screens use Connect's own tokens, read from a saved page of the
  platform: palette, type scale, radii, motion. They're built as a tab inside
  a Circle, with Connect's chrome as a static frame.

## Where AI was used

Everything in `backend/`, `frontend/`, and `db/` was generated with Claude
Code (Claude Fable 5) from `docs/spec.md`, then read, run, and edited by me.
The research reading above was Claude Code fetching pages and articles into
notes. The design tokens came from Claude Code reading Connect's stylesheet
out of a page I saved while signed in. The prose in `docs/` is mine.

## Time

The spec and the backend fit the 2 to 3 hour box. The screens were an
afternoon on top, because the round-one note asked for a couple of screens
that look great and actually function, and the document asked for a backend.
I built both.

## Tools

Claude Code, Docker, Postgres 16, Python 3.12, FastAPI, psycopg, pytest, uv.
