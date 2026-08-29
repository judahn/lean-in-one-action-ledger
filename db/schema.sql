-- One Action Ledger, Postgres 16
-- Readable top to bottom like the Supabase SQL editor.

create extension if not exists "pgcrypto";

create type action_status as enum ('committed', 'done', 'partly', 'not_yet');

create table circles (
  id          uuid primary key default gen_random_uuid(),
  name        text not null,
  created_at  timestamptz not null default now()
);

create table members (
  id            uuid primary key default gen_random_uuid(),
  display_name  text not null,
  email         text not null unique,
  created_at    timestamptz not null default now()
);

create table memberships (
  circle_id   uuid not null references circles(id) on delete cascade,
  member_id   uuid not null references members(id) on delete cascade,
  role        text not null default 'member' check (role in ('member', 'leader')),
  joined_at   timestamptz not null default now(),
  primary key (circle_id, member_id)
);

create table meetings (
  id                   uuid primary key default gen_random_uuid(),
  circle_id            uuid not null references circles(id) on delete cascade,
  held_at              timestamptz not null,
  moderator_member_id  uuid references members(id),
  created_at           timestamptz not null default now(),
  unique (circle_id, held_at)
);

-- "last N meetings" and "next meeting" for a Circle
create index meetings_circle_held_at on meetings (circle_id, held_at desc);

create table actions (
  id          uuid primary key default gen_random_uuid(),
  meeting_id  uuid not null references meetings(id) on delete cascade,
  member_id   uuid not null references members(id) on delete cascade,
  -- denormalized from meetings.circle_id so the check-in hits one index.
  -- The application enforces it matches the meeting's Circle (spec, invariant 2).
  circle_id   uuid not null references circles(id) on delete cascade,
  text        text not null,
  why         text,
  status      action_status not null default 'committed',
  created_at  timestamptz not null default now(),
  -- invariant 1: one action per member per meeting
  unique (meeting_id, member_id)
);

-- the check-in's hot path: a Circle's actions across its last few meetings
create index actions_circle_meeting on actions (circle_id, meeting_id);
-- a member's own view, and "what's still open for me"
create index actions_member_status on actions (member_id, status);
-- carry-over query: open actions without scanning finished ones
create index actions_open on actions (circle_id) where status = 'committed';

create table action_updates (
  id          uuid primary key default gen_random_uuid(),
  action_id   uuid not null references actions(id) on delete cascade,
  status      action_status not null check (status <> 'committed'),  -- invariant 3
  note        text,
  created_at  timestamptz not null default now()
);

create index action_updates_action_created on action_updates (action_id, created_at desc);
