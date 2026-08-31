# One Action Ledger, spec

Lean In round 1 take-home. The spec is the contract the code is built
against. Anything not in here is out of scope for the 2-3 hour box and goes
under "what I'd do next" in the design doc.

## The feature in one paragraph

Every Lean In Circle meeting ends with each member committing to one
concrete thing she'll do before the next meeting (Lean In's "One Action").
Today that commitment lives on a printed worksheet and the follow-through
happens on email or a Facebook group. The ledger is the platform holding it:
a member records her action, marks it done or not between meetings, and the
moderator opens the next meeting with the One Action Update already
assembled. The same page is where the meeting closes: the next round of
commitments lands on it as the room says them out loud. No new ritual. Their
ritual, made to work between meetings.

## Ubiquitous language (Lean In's own words, nothing renamed)

- **Circle**: a small peer group (8-12) that meets regularly.
- **Member**: a person in one or more Circles.
- **Meeting**: one gathering of a Circle, ordered by date.
- **One Action** (`Action`): a member's single commitment made at a meeting,
  due by the next one.
- **Update** (`ActionUpdate`): a member's report on an action between
  meetings: done, partly, not yet, with an optional note.
- **Moderator**: the member running a given meeting (rotates).
- **One Action Update** (`CheckIn`): the assembled read for the moderator
  opening the next meeting.

## Domain model (bounded context: Circle Commitments)

**Aggregates.** `Circle` is the root and owns its `Meetings`. `Meeting` owns
its `Actions`. Invariants the aggregate enforces, not the database alone:

1. One action per member per meeting.
2. An action's member must be a member of the action's Circle.
3. Status only moves forward from `committed` (to `done`, `partly`, or
   `not_yet`). A later update can revise among those three, never back to
   `committed`.
4. A report freezes the wording. An action's text and why change only while
   its status is `committed`, which by rule 3 means only before the first
   report. What the Circle heard stays what the Circle heard.

Rules 1 and 3 are backed by constraints in the schema. Rules 2 and 4 are
enforced in the application only.

**Entities:** Circle, Member, Meeting, Action.
**Value objects:** `ActionStatus` (committed | done | partly | not_yet),
`FollowThroughRate` (computed, never stored), `CheckIn` (a read model).
**Domain service:** `CheckInAssembler`: pure function over a Circle and its
last N meetings, produces a `CheckIn`. No I/O. Unit-tested on its own.
**Built pairing with Judah, rule by rule. The piece he explains in the
interview.**
**Services:** `ActionService` (record, update, list for a member) and
`CheckInService` (loads the Circle's recent meetings, runs the assembler,
adds the opener). Thin, transactional, no domain logic. No use-case layer.
**Infrastructure:** repository interfaces live in the domain, psycopg
implementations sit against Postgres, and FastAPI routers map HTTP to services.

Folder shape:

```
backend/
  app/
    domain/         entities, value objects, CheckInAssembler, repository interfaces
    services/       ActionService, CheckInService, opener_prompt.md
    infrastructure/ postgres repositories, db connection
    api/            FastAPI app and routers
  tests/
    conftest.py                   test database, seed, TestClient
    domain/test_invariants.py     the aggregate rules, no DB
    domain/test_check_in.py       the assembler, from the example response below
    infrastructure/test_schema.py the constraints that back the invariants
    api/test_endpoints.py         one per endpoint, check-in asserts the example
  pyproject.toml, uv.lock
frontend/         Next.js + Tailwind. The screens, specified below once decided.
db/
  schema.sql      the schema, readable like the Supabase SQL editor
  seed.sql        one Circle, eight members, three past meetings, one next
docker-compose.yml
docs/
  spec.md design.md schema.md process.md
```

## Schema (Postgres, see `db/schema.sql` for the exact DDL)

| Table | Purpose | Notes |
|---|---|---|
| `circles` | the Circle | `id`, `name` |
| `members` | a person | `id`, `display_name`, `email` unique |
| `memberships` | who is in which Circle | pk `(circle_id, member_id)`, `role` in (member, leader) |
| `meetings` | one gathering | `circle_id`, `held_at`, `moderator_member_id` nullable, unique `(circle_id, held_at)` |
| `actions` | the One Action | `meeting_id`, `member_id`, `circle_id` (denormalized, see below), `text`, `why` nullable, `status`, unique `(meeting_id, member_id)` |
| `action_updates` | the history of a member's reports on an action | `action_id`, `status`, `note` nullable, `created_at`. `actions.status` holds the current value |

`action_status` is a Postgres enum: `committed`, `done`, `partly`, `not_yet`.

**Indexes, and why:**
- `actions (circle_id, meeting_id)`: the check-in reads a Circle's actions
  across its last few meetings. This is the hot path.
- `actions (member_id, status)`: a member's own view, and "what's still open
  for me."
- partial index `actions (circle_id) WHERE status = 'committed'`: the
  carry-over query (open actions from older meetings) without scanning
  finished ones.
- `meetings (circle_id, held_at DESC)`: "last N meetings" and "next meeting."

**Why `circle_id` is denormalized onto `actions`:** the check-in is always
per Circle, and putting `circle_id` on the row means the hot query hits one
index instead of joining through `meetings`. The service layer enforces that it
matches the meeting's Circle (invariant 2). At scale a trigger or a generated
column would enforce it in the database too. Noted in the design doc.

## API

Identity is out of scope for the take-home (no auth, no sessions). Requests
carry `X-Member-Id` to say who is asking, and the service checks
that member belongs to the Circle. The design doc says how real auth and
row-level policies would replace this at scale.

### `POST /circles/{circle_id}/meetings/{meeting_id}/actions`
Record a One Action. Body: `{ "text": string, "why": string | null }`.
Member comes from `X-Member-Id`. 201 with the action. 409 if that member
already has an action for that meeting (invariant 1). 403 if not a member.

### `PATCH /actions/{action_id}`
Report on an action, or reword it. The body carries one intent or the other.

`{ "status": "done" | "partly" | "not_yet", "note": string | null }` reports.
It appends an `action_update` and sets `actions.status`. 422 if status is
`committed` (invariant 3).

`{ "text": string, "why": string | null }` rewords, and only while the action
is still `committed`. 422 once a report exists (invariant 4).

Only the action's own member may do either (403 otherwise). A body carrying
neither intent, or both, is 422.

### `GET /members/{member_id}/actions`
A member's own history, newest first. Only that member (403 otherwise).

### `GET /circles/{circle_id}/meetings/next/check-in` (the one that does real work)
Assembles the One Action Update for the moderator opening the next meeting.
Any member of the Circle may read it (that mirrors the room: the update is
read aloud). Query params: `window` (default 3) = how many past meetings the
follow-through rate covers. `as_of` (ISO datetime, default now) fixes the
clock, so the demo and the tests don't depend on the wall clock.

The response carries two lists, in the order the meeting uses them. `actions`
is what the room reports on: last meeting's commitments, plus anything still
open from earlier. `upcoming` is what the room commits to before it leaves,
the next meeting's actions, so the closing go-around lands on the page as it
happens. An upcoming entry can already carry a status other than `committed`,
because a member may report before the meeting. Entries in both lists have the
same fields. `why` is a member's note to herself and stays on her own page.

Example response:

```json
{
  "circle": { "id": "…", "name": "West Coast Execs" },
  "next_meeting": { "id": "…", "held_at": "2026-09-10T18:00:00-07:00", "moderator": { "id": "…", "display_name": "Dana" } },
  "since_meeting": { "id": "…", "held_at": "2026-08-13T18:00:00-07:00" },
  "actions": [
    {
      "member": { "id": "…", "display_name": "Lena" },
      "text": "Book the informational with the VP of Ops",
      "status": "committed",
      "note": null,
      "committed_at": { "id": "…", "held_at": "2026-07-09T18:00:00-07:00" },
      "carried_over": true
    },
    {
      "member": { "id": "…", "display_name": "Priya" },
      "text": "Ask Marcus for the Q4 launch to lead",
      "status": "done",
      "note": "Asked Tuesday. He said yes.",
      "committed_at": { "id": "…", "held_at": "2026-08-13T18:00:00-07:00" },
      "carried_over": false
    }
  ],
  "upcoming": [
    {
      "member": { "id": "…", "display_name": "Grace" },
      "text": "Put my name forward for the exec sponsor program",
      "status": "committed",
      "note": null,
      "committed_at": { "id": "…", "held_at": "2026-09-10T18:00:00-07:00" },
      "carried_over": false
    }
  ],
  "follow_through": {
    "window_meetings": 3,
    "committed": 24,
    "done": 15,
    "partly": 4,
    "not_yet": 3,
    "open": 2,
    "rate": 0.71
  },
  "opener": "15 of 24 actions landed over the last 3 meetings. 2 are carried over from earlier meetings.",
  "opener_source": "template"
}
```

**Ordering rule:** carried-over actions (status `committed` or `not_yet`,
from meetings inside the window and before `since_meeting`) come first,
oldest meeting first. Then this meeting's actions, alphabetically by
member. `upcoming` is alphabetical by member too. Ties read alphabetically
everywhere. The tool remembers, it
doesn't rank: grouping by status is a switch on the page, the moderator's
call, so the product stays out of the "wins first or go around the room"
argument.

**Follow-through rate:** `(done + 0.5 × partly) / committed_in_window`,
rounded to two places. `partly` counts as half on purpose: the ritual
rewards movement, not perfection. Documented, easy to change.

**Opener:** a deterministic template by default that states the numbers
and stops: "15 of 24 actions landed over the last 3 meetings. 2 are carried
over from earlier meetings." Behind `OPENER_AI=1`, the same facts go to
Claude with a short prompt (`app/services/opener_prompt.md`) and the
returned line replaces the template. If Claude is unreachable or declines,
the template stands. The response includes
`"opener_source": "template" | "claude"`. This is the only place AI touches
the product, and it's optional.

## Tests (TDD, scoped to what would break if changed)

Test first, but not everything. The test is written before the code it
protects, for the things a later change could silently break:

- The invariants, as unit tests on the aggregate with no database.
- `CheckInAssembler`, as unit tests built from the example response above:
  ordering, carry-over, the upcoming group, the rate, the template opener
  and `opener_source`.
- The schema constraints that back rules 1 and 3, one integration test
  each, so the database still refuses what the aggregate refuses.
- One test per endpoint. The check-in endpoint asserts the example shape.

Not tested: FastAPI wiring, Pydantic serialization, seed content, the AI
opener (the flag stays off in tests). Each test is named for the rule it
protects and checks one behavior, so a failure reads as a sentence.

## Privacy rules (the design judgment, stated as requirements)

- A member sees only her own history.
- The check-in is visible to the Circle's members, because the room hears it
  anyway. It never includes per-member rates, streaks, or rankings. Only the
  Circle-level rate is computed.
- No endpoint lists a member's actions to anyone but her.
- Nothing is exposed across Circles.

## Seed data (`db/seed.sql`)

One Circle ("West Coast Execs"), eight members, three past meetings (July,
August, and one in June) with actions in a realistic mix of statuses, two
carried-over actions, one scheduled next meeting in September with a
moderator set and two actions already committed for it. Enough that the check-in response is interesting on first run.

## Setup (README target)

```
docker compose up -d                          # Postgres 16, applies db/schema.sql and db/seed.sql
cd backend && uv sync && uv run pytest        # 16+ tests against a throwaway ledger_test database
uv run uvicorn app.api.main:app --reload      # API on :8000
cd ../frontend && npm install && npm run dev  # screens on :3000
```

Then `GET http://localhost:8000/circles/{seed_circle_id}/meetings/next/check-in`
with `X-Member-Id: {seed_member_id}` (both printed by the seed step).

## Time box (theirs: 2-3 hours)

- 0:00-0:30 Judah edits this spec: names, invariants, exclusions. Decisions.
- 0:30-1:00 Claude Code writes the invariant tests first (red), then the
  entities and `schema.sql` that turn them green, then the rest of the
  scaffold: `seed.sql`, docker-compose, repositories, routers with their
  endpoint tests, README. Judah reads the tests as the spec in executable
  form, then the code.
- 1:00-1:30 **`CheckInAssembler`, paired** (ordering, carry-over, rate,
  template opener): Claude Code writes tests from the spec's example first,
  then the assembler one rule at a time while Judah reads and questions
  each one.
- 1:30-2:00 Judah reviews every file, runs tests, fixes.
- 2:00-2:30 `design.md` and `schema.md` in Judah's words from this spec and
  what changed, and `process.md` filled in by Judah.
- Stop. Anything left goes under "what I'd do next."

## What I'd do next (design doc material, not built)

- **Pulse**: attendance + follow-through + a post-meeting energy check → a
  Circle health read with one nudge linking to the matching Lean In leader
  resource. Same schema, one more endpoint, a nightly snapshot table instead
  of read-time aggregation.
- Real identity: Supabase Auth or equivalent, row-level policies replacing
  the `X-Member-Id` header, moderator role on `memberships` per meeting.
- Nudges between meetings (email, since that's where Circles already live).
- A trigger or generated column enforcing `actions.circle_id`.
- Multi-Circle members and Networks are already representable, untested.
