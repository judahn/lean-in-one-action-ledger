# Schema

Postgres 16. The DDL is `db/schema.sql`, written to read top to bottom. This
is the walk-through: what each table is for, where the invariants live, and
why each index exists.

## Tables

| Table | One row is | Notes |
|---|---|---|
| `circles` | a Circle | `id`, `name` |
| `members` | a person | `email` is unique |
| `memberships` | a person in a Circle | primary key `(circle_id, member_id)`, `role` is `member` or `leader` |
| `meetings` | one gathering of a Circle | `held_at`, optional `moderator_member_id`, unique `(circle_id, held_at)` |
| `actions` | a member's One Action from a meeting | `text`, optional `why`, `status`, and `circle_id` denormalized |
| `action_updates` | one report on an action | `status`, optional `note`, `created_at`. Append only |

`action_status` is an enum: `committed`, `done`, `partly`, `not_yet`.
`actions.status` holds the current value so the Update never has to fold the
history. `action_updates` is the history: the front-end shows the latest note
from it, and a member's page of reports could read it in full.

Ids are UUIDs from `pgcrypto`. Everything cascades from its parent, so
deleting a Circle takes its meetings and actions with it.

## Where the invariants live

The domain enforces the four rules from the spec. The schema backs two of
them so a write that bypasses the domain still can't break them.

1. **One action per member per meeting**: `unique (meeting_id, member_id)`
   on `actions`.
2. **The member belongs to the Circle**: enforced in the aggregate today.
   The database can't express it as a constraint across three tables without
   a trigger. See "At scale."
3. **Status never returns to committed**: `check (status <> 'committed')` on
   `action_updates`. A report is always forward.
4. **A report freezes the wording**: enforced in the aggregate. Text and why
   change only while the action is still `committed`. Only the application
   knows a reword from a report, so at scale a trigger closes this one
   alongside rule 2.

Both backed rules have a test that inserts past the domain and expects the
database to refuse.

## Indexes, and the query each one serves

- `meetings (circle_id, held_at desc)`: "the next meeting" and "the last N
  meetings" for a Circle. Both read this index in order.
- `actions (circle_id, meeting_id)`: the Update's hot path, one Circle's
  actions across its last few meetings, as a single `= any(...)` query.
- `actions (member_id, status)`: a member's own history, and "what's still
  open for me."
- `actions (circle_id) where status = 'committed'`: a partial index for the
  carry-over query in the version that carries forever. Today the carry-over
  stays inside the window and rides the hot-path index. The partial index is
  small and cheap to keep for the day a Circle wants the longer memory.
- `action_updates (action_id, created_at desc)`: the latest report for an
  action, which is the note the Update shows.

## Why `circle_id` is on `actions`

The Update is always per Circle. Without `circle_id` on the row, the hot
query joins `actions` to `meetings` to filter by Circle. With it, the query
hits one index and the join disappears. The cost is one column that could
disagree with `meetings.circle_id`. The service sets it from the meeting and
the aggregate checks it. At scale a `before insert` trigger or a generated
column closes the gap in the database.

## What is deliberately not here

- No identity, sessions, or auth tables. `X-Member-Id` stands in, and real
  auth arrives as row-level security on these same tables.
- No `circle.timezone`. The seed Circle meets on the West Coast and the
  front-end knows that. A real Circle carries its own.
- No precomputed Update. Read-time assembly is right at this size. See below.
- No soft deletes, no audit columns beyond `created_at`. Nothing here needed
  them yet.

## At scale

At 150,000 Circles meeting monthly with ten members, this is roughly 18
million `actions` rows a year and about the same in `action_updates`. Every
read is per Circle and per member, so the indexes above keep each query to
tens of rows. What changes:

- A nightly snapshot table for the Update, keyed by `(circle_id, meeting_id)`,
  for Circles with a meeting in the next week. The read-time path stays for
  anything that changed since.
- The trigger or generated column on `actions.circle_id`.
- Row-level security once there's real identity.
- Partitioning `actions` by year would be the next step after that, and it's
  years out.
