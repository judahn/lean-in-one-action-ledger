# One Action Ledger

Every Lean In Circle meeting ends with each member committing to one concrete
thing she'll do before the next meeting. Lean In calls it the One Action.
Today it lives on a printed worksheet and the follow-up happens on email. This
is the platform holding it: a member records her action, marks it done or not
between meetings, and the moderator opens the next meeting with the One Action
Update already assembled.

Built as a tab inside Lean In Connect, using Connect's own design tokens.

## What's here

```
backend/    FastAPI + psycopg on Postgres. Domain, services, repositories, API. 29 tests.
frontend/   Next.js + Tailwind. Two screens: the Circle's One Action Update, and My actions.
db/         schema.sql (the schema, with index rationale) and seed.sql (one Circle, eight members).
docs/       spec.md (the contract), design.md, schema.md, process.md (how AI was used).
```

## Run it

You need Docker Desktop, [uv](https://docs.astral.sh/uv/), and Node 20 or newer.

```
docker compose up -d --wait                 # Postgres 16 on :5433, schema and seed applied
cd backend && uv sync && uv run pytest      # 29 tests against a throwaway ledger_test database
uv run uvicorn app.api.main:app --reload    # API on :8000, docs at /docs
cd ../frontend && npm install && npm run dev  # screens on :3000
```

Open http://localhost:3000. It lands on the Circle's One Action tab.

## Try it

You start as Priya. The **Circle update** is what the moderator reads to open
the September 10 meeting: what's still open from earlier meetings, then
August's actions alphabetically (sort by status is the moderator's switch),
the counts, and a one-line opener.

- Click the avatar top right and pick **Yuki**. Her June action is still
  open. Under **My actions**, mark it done with a line about it, then go back
  to the Circle update and find it.
- As anyone, record your One Action for September 10 under **My actions**.
  It shows in your rail on the Circle update with a note on when it reads
  out (October, since the Update reads the previous meeting's commitments).
- Pick **Dana** to see the leader tag. She moderates September's meeting.

The switcher is a cookie that becomes the `X-Member-Id` header. Identity is
out of scope for the take-home. `docs/design.md` says how real auth replaces it.

The API directly:

```
curl -H 'X-Member-Id: a0000000-0000-4000-8000-000000000001' \
  'http://localhost:8000/circles/c0000000-0000-4000-8000-000000000001/meetings/next/check-in?as_of=2026-08-29T12:00:00Z'
```

`as_of` fixes the clock so the demo doesn't depend on today's date. Without
it the API uses now, and the seed's next meeting is September 10, 2026.

## Reset the data

The seed runs when the database is first created. To get back to a clean
Circle after poking at it:

```
docker compose down -v && docker compose up -d --wait
```

To see the empty states, before anyone has recorded an action, clear the
actions and keep the Circle, members, and meetings:

```
docker compose exec db psql -U ledger -d ledger -c "truncate actions cascade"
```

## Settings

All optional. Defaults work for the local setup above.

| Variable | Where | Default | What it does |
|---|---|---|---|
| `DATABASE_URL` | backend | `postgresql://ledger:ledger@localhost:5433/ledger` | the API's database |
| `TEST_DATABASE_URL` | backend | `...:5433/ledger_test` | rebuilt by the test suite |
| `API_URL` | frontend | `http://localhost:8000` | where the screens fetch from |


## Working on it

- `backend/`: `uv run pytest`, `uv run ruff check app tests`, `uv run ruff format app tests`.
- `frontend/`: `npm run lint`, `npx tsc --noEmit`. After an API change,
  `npm run api:types` regenerates `lib/api/types.ts` from `openapi.json`
  (dump a fresh one from the running API at `/openapi.json`).
- Type sizes, colors, radii: `frontend/app/globals.css`, one place.

## Read next

`docs/spec.md` is the contract the code was built against. `docs/design.md`
has the tradeoffs and what changes at scale. `docs/schema.md` walks the
tables and indexes. `docs/process.md` says how AI was used, and where.
