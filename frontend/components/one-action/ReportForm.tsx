"use client";

import { useActionState, useState } from "react";
import { reportAction, type FormState } from "@/app/actions";
import type { Action, ActionStatus } from "@/lib/api/client";

const CHOICES: { value: ActionStatus; label: string; on: string }[] = [
  {
    value: "done",
    label: "Done",
    on: "border-emerald bg-tint-green text-emerald",
  },
  {
    value: "partly",
    label: "Partly",
    on: "border-[#6c3a05] bg-tint-orange text-[#6c3a05]",
  },
  {
    value: "not_yet",
    label: "Not yet",
    on: "border-burgundy bg-tint-poppy text-burgundy",
  },
];

export function ReportForm({ action }: { action: Action }) {
  const [state, submit, pending] = useActionState<FormState, FormData>(
    reportAction,
    {},
  );
  const [status, setStatus] = useState<ActionStatus | null>(
    action.status === "committed" ? null : action.status,
  );
  return (
    <form action={submit} className="mt-3">
      <div className="flex flex-wrap gap-2">
        {CHOICES.map((c) => (
          <label
            key={c.value}
            className={`type-label flex h-8 cursor-pointer items-center rounded-full border px-3 motion-fast ${
              status === c.value
                ? c.on
                : "border-warm-300 text-warm-500 hover:bg-warm-200"
            }`}
          >
            <input
              type="radio"
              name="status"
              value={c.value}
              checked={status === c.value}
              onChange={() => setStatus(c.value)}
              className="sr-only"
              required
            />
            {c.label}
          </label>
        ))}
      </div>
      <input type="hidden" name="action_id" value={action.id} />
      <div className="mt-3 flex flex-wrap items-center gap-2">
        <input
          name="note"
          defaultValue={action.note ?? ""}
          placeholder="One line about how it went"
          className="type-body h-9 min-w-[260px] flex-1 rounded-md border border-warm-400 bg-warm-50 px-3 outline-none focus:border-orange focus:ring-2 focus:ring-orange/30"
        />
        <button
          type="submit"
          disabled={pending || !status}
          className="btn btn-dark disabled:opacity-40"
        >
          {pending ? "Saving…" : "Save"}
        </button>
        {state.error && (
          <span className="type-caption text-red">{state.error}</span>
        )}
      </div>
    </form>
  );
}
