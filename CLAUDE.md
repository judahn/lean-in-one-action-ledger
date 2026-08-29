# One Action Ledger

`docs/spec.md` is the contract. Build against it, don't extend it. Time box
is 2-3 hours, so a focused feature that works beats an ambitious one that
doesn't.

## Stack (fixed)

Postgres 16 in Docker, `db/schema.sql` and `db/seed.sql` as plain SQL,
psycopg (v3) behind repository classes, FastAPI, pytest, uv. No ORM, no
extra services.

## Layers

DDD, kept light. `app/domain` holds entities, value objects, repository
interfaces, and `CheckInAssembler`. `app/services` is thin and
transactional: it orchestrates domain and repositories and holds no domain
logic. No use-case layer. `app/infrastructure` has the Postgres repositories
and the connection. `app/api` is FastAPI. The domain has no I/O and no
framework imports.

## Rules

- Invariants from the spec are enforced in the aggregate and backed by
  constraints in the schema: one action per member per meeting, member
  belongs to the Circle, status only moves forward from `committed`.
- Privacy rules in the spec are requirements. No endpoint exposes
  per-member rates or rankings.
- `CheckInAssembler` is built one rule at a time, paired: state the rule,
  write its test from the spec's example response, write the function, read
  it back before the next rule. Small and plain.
- TDD, scoped to what would break if changed. The test comes before the
  code it protects, for: the three invariants (unit, no DB),
  `CheckInAssembler` (unit), the schema constraints that back the
  invariants (against the Docker Postgres), and one test per endpoint, with
  the check-in endpoint asserting the example shape. Not tested: framework
  wiring, serialization, seed content, the AI opener (flag off in tests).
- A test is named for the rule it protects, checks one behavior, and drives
  the public surface (a service or domain method), never a private helper.
  Mock only at I/O (repositories, the LLM), never the domain. A bug found
  later gets a failing test before the fix.
- A module past about 200 lines is split by responsibility before anything
  is added to it. A function fits on one screen. Plain over clever.
- Decisions worth a sentence go in `docs/process.md`.
- Docs: no em dashes, no semicolons. Plain sentences.
- `uv run pytest` passes before anything is called done.
