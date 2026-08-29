"use client";

import { useState } from "react";
import type { ActionStatus, CheckInAction } from "@/lib/api/client";
import { meetingDay, meetingMonth } from "@/lib/format";
import { Avatar } from "./Avatar";
import { StatusPill } from "./StatusPill";

type Sort = "name" | "status";
const STATUS_ORDER: Record<ActionStatus, number> = { done: 0, partly: 1, not_yet: 2, committed: 3 };

/** The wall. Alphabetical by default. The status sort is the moderator's choice, not the tool's. */
export function UpdateList({
  actions,
  sinceHeldAt,
}: {
  actions: CheckInAction[];
  sinceHeldAt: string | null;
}) {
  const [sort, setSort] = useState<Sort>("name");
  const carried = actions.filter((a) => a.carried_over);
  const thisMeeting = actions.filter((a) => !a.carried_over);
  const ordered =
    sort === "status"
      ? [...thisMeeting].sort((a, b) => STATUS_ORDER[a.status] - STATUS_ORDER[b.status])
      : thisMeeting;

  return (
    <div>
      <div className="flex items-center justify-between">
        <h3 className="type-overline text-burgundy">Latest actions</h3>
        <div className="type-label-sm flex items-center gap-0.5 rounded-full bg-warm-200 p-0.5">
          {(["name", "status"] as Sort[]).map((s) => (
            <button
              key={s}
              type="button"
              onClick={() => setSort(s)}
              className={`h-6 rounded-full px-2.5 transition-colors ${
                sort === s ? "bg-warm-50 text-warm-900 shadow-card" : "text-warm-500"
              }`}
            >
              By {s}
            </button>
          ))}
        </div>
      </div>

      {carried.length > 0 && (
        <Group title="Still open from earlier meetings">
          {carried.map((a) => (
            <Row key={a.member.id + a.committed_at.id} action={a} since={`committed in ${meetingMonth(a.committed_at.held_at)}`} />
          ))}
        </Group>
      )}
      {sinceHeldAt && (
        <Group title={`From ${meetingDay(sinceHeldAt)}`}>
          {ordered.map((a) => (
            <Row key={a.member.id + a.committed_at.id} action={a} />
          ))}
        </Group>
      )}
      {actions.length === 0 && (
        <p className="type-body mt-4 text-warm-500">No One Actions on the ledger yet.</p>
      )}
    </div>
  );
}

function Group({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="mt-4">
      <div className="type-caption text-warm-500">{title}</div>
      <ul className="mt-1 divide-y divide-warm-200">{children}</ul>
    </div>
  );
}

function Row({ action, since }: { action: CheckInAction; since?: string }) {
  return (
    <li className="flex items-start gap-3 py-3">
      <Avatar id={action.member.id} name={action.member.display_name} />
      <div className="min-w-0 flex-1">
        <div className="type-caption text-warm-500">
          <span className="font-semibold text-warm-900">{action.member.display_name}</span>
          {since && ` · ${since}`}
        </div>
        <div className="type-body font-semibold">{action.text}</div>
        {action.note && <div className="type-body text-warm-500">{action.note}</div>}
      </div>
      <StatusPill status={action.status} />
    </li>
  );
}
