"use client";

import { useActionState } from "react";
import { recordAction, type FormState } from "@/app/actions";

const FIELD =
  "type-input mt-1.5 w-full rounded-md border border-warm-400 bg-warm-50 px-3 py-2 outline-none focus:border-orange focus:ring-2 focus:ring-orange/30";

export function RecordForm({ circleId, meetingId }: { circleId: string; meetingId: string }) {
  const [state, action, pending] = useActionState<FormState, FormData>(recordAction, {});
  return (
    <form action={action} className="mt-3 rounded-lg border border-warm-300 p-4">
      <input type="hidden" name="circle_id" value={circleId} />
      <input type="hidden" name="meeting_id" value={meetingId} />
      <label className="type-label block">
        What&apos;s the one thing you&apos;ll do before the next meeting?
        <textarea name="text" rows={2} required placeholder="Ask Marcus for the Q4 launch to lead" className={FIELD} />
      </label>
      <label className="type-label mt-3 block">
        Why it matters <span className="font-normal text-warm-500">(optional)</span>
        <input name="why" placeholder="The cycle closes in October" className={FIELD} />
      </label>
      <div className="mt-4 flex items-center gap-3">
        <button
          type="submit"
          disabled={pending}
          className="type-label h-9 rounded-full bg-burgundy px-4 text-warm-100 transition-opacity disabled:opacity-60"
        >
          {pending ? "Recording…" : "Commit to it"}
        </button>
        {state.error && <span className="type-caption text-red">{state.error}</span>}
      </div>
    </form>
  );
}
