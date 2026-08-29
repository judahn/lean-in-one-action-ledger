// The seed Circle and its members, from db/seed.sql. Identity is out of scope for
// the take-home, so the member switcher in the top bar stands in for sign-in.

export const SEED_CIRCLE_ID = "c0000000-0000-4000-8000-000000000001";

export const SEED_MEMBERS = [
  { id: "a0000000-0000-4000-8000-000000000001", name: "Priya" },
  { id: "a0000000-0000-4000-8000-000000000002", name: "Lena" },
  { id: "a0000000-0000-4000-8000-000000000003", name: "Dana" },
  { id: "a0000000-0000-4000-8000-000000000004", name: "Marisol" },
  { id: "a0000000-0000-4000-8000-000000000005", name: "Grace" },
  { id: "a0000000-0000-4000-8000-000000000006", name: "Yuki" },
  { id: "a0000000-0000-4000-8000-000000000007", name: "Tamar" },
  { id: "a0000000-0000-4000-8000-000000000008", name: "Nadia" },
] as const;

export const CIRCLE_LEADER_ID = SEED_MEMBERS[2].id; // Dana

// The demo clock. The seed's next meeting is September 10, 2026, so the Update
// stays meaningful whenever the reviewer runs it.
export const DEMO_AS_OF = "2026-08-29T12:00:00Z";
