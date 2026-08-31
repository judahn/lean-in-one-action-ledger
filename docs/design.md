# One Action Ledger, design

## What it is

Every Lean In Circle meeting ends with each member committing to one concrete
thing she'll do before the next meeting. Lean In calls it the One Action, it's
in the Circle meeting guide, and the next meeting is supposed to open with
everyone's update on it. Today the commitment lives on a printed worksheet and
the follow-through happens on email or a Facebook group. The platform doesn't
hold any of it.

This is the platform holding it. A member records her action at the end of the
meeting, marks it done, partly, or not yet between meetings, and the moderator
opens the next meeting with the One Action Update already assembled. No new
ritual to teach a Circle. Their ritual, made to work between meetings.

## Two moments, two screens

The ritual has a write moment and a read moment, so the feature has two
screens, built as a One Action tab inside a Circle in Lean In Connect.

**My actions** is the write side and it's private: record your One Action,
mark the open one done or not with a line about it, see your own history.

**The Circle update** is the read side and it's shared: what's still open from
earlier meetings, then this meeting's actions, the counts over the last three
meetings, and a one-line opener the moderator can read or ignore. Every member
sees the same page, because the room hears it read aloud anyway.

## The model

One bounded context, Circle Commitments. `Circle` is the aggregate root and
owns its `Meetings`. `Meeting` owns its `Actions`. Three invariants are
enforced in the aggregate and backed by the schema:

1. One action per member per meeting.
2. An action's member belongs to the action's Circle.
3. Status only moves forward from `committed`. A later report can revise among
   done, partly, and not yet, never back.

`CheckInAssembler` is a pure domain service: given a Circle, its next meeting,
and its last N meetings with their actions, it produces the Update. No I/O, so
it's unit-tested from the example response in the spec, rule by rule. Services
(`ActionService`, `CheckInService`) are thin and transactional. Repositories
are protocols in the domain with psycopg implementations underneath. FastAPI
maps HTTP to services and maps domain errors to status codes in one place.

The front-end is Next.js server components reading the API with the member's
id in a header, and server actions for the two writes. Its types are generated
from the API's OpenAPI document, never hand-written, so the Pydantic models are
the one contract.

## What it refuses to do

This is the design judgment, and it's in the spec as requirements rather
than left to taste.

- No per-member rates, streaks, or rankings exist anywhere. The only rate is
  the Circle's.
- The Update lists this meeting's actions alphabetically. Grouping by status
  is a switch on the page, the moderator's choice. The tool remembers, it
  doesn't rank, and it stays out of the "wins first or go around the room"
  argument.
- The counts come first and the rate is small. A Circle is not a scoreboard.
- A month with nothing committed has no rate, rather than a zero that reads as
  a bad month.
- The opener states the numbers and stops. Warmth is the moderator's.
- A member sees her own history and nobody else's. Nothing crosses Circles.

## Tradeoffs I made on purpose

- **Postgres in Docker, plain `schema.sql`, psycopg, no ORM.** The assignment
  grades the schema and the indexing, and those are a Postgres story. Every
  query in the repo is readable and explainable.
- **`circle_id` denormalized onto `actions`.** The Update is always per
  Circle. With `circle_id` on the row, the hot query hits one index instead
  of joining through `meetings`. The service enforces that it matches the
  meeting's Circle. At scale a trigger or generated column does it in the
  database too.
- **Carry-over stays inside the window.** The rate and the carry-over share
  one horizon (three meetings by default), so the moderator's list stays
  bounded. The partial index on open actions is there for the version that
  carries forever, if a Circle wants it.
- **The Update reads the previous meeting's commitments.** An action recorded
  for the upcoming meeting shows in your own rail with a note on when it reads
  out. The wall never shows a Circle promises nobody has made out loud yet.
- **Identity is a header.** `X-Member-Id` says who is asking and the service
  checks membership. The member switcher in the top bar sets it. Real auth
  replaces both without touching the domain.
- **`as_of` on the check-in.** The demo and the tests don't depend on the wall
  clock.
- **Connect's own design tokens.** The screens use Lean In Connect's palette,
  type scale, radii, and motion, read from a saved page of the platform, so
  the tab looks like it belongs there. The whole scale is twenty lines in one
  CSS file.
- **Seeded, not modeled.** The Circle's name, members, and timezone come from
  the seed on the front-end. There is no Circle endpoint in the spec and I
  didn't add one.

## At scale

Lean In has 150,000 Circles. At 8 to 12 members meeting monthly, that's on
the order of 18 million actions a year. Postgres handles that comfortably
with the indexes in the schema, because every read is per Circle and touches
tens of rows, not millions.

- **Reads.** The Update is assembled at request time today. At scale it's a
  nightly precompute per Circle with a meeting in the next week, stored as a
  snapshot row, with the request-time path kept for Circles that changed
  since. Member history paginates.
- **Integrity.** A trigger or generated column enforces `actions.circle_id`.
  Row-level security policies replace the header once there's real identity
  (Supabase Auth or equivalent), with the moderator as a role on the meeting.
- **Ops.** `schema.sql` stays the source of truth and every migration updates
  it. Structured logs on the service layer, an alert on assembler latency.

## What I'd do next

- An opt-in AI opener. Claude writes the moderator's line from the same
  facts the Update already shows, nightly through the Batches API for
  Circles with a meeting coming up. Designed and cut from round one, so the
  demo needs no key.
- **Pulse**: attendance, follow-through, and a post-meeting energy check, read
  as a Circle health snapshot with one nudge linking to the matching leader
  resource. Same schema, one more endpoint.
- Rewording a commitment before you've reported on it. A report freezes the
  wording. One more invariant, one more test.
- Nudges between meetings, on email, since that's where Circles already live.
- A per-Circle timezone, and a Circle endpoint so the front-end stops reading
  the seed.
- Multi-Circle members and Networks are already representable, and untested.

