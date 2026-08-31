"use client";

import { useState, useTransition } from "react";
import { rewriteAction } from "@/app/actions";
import type { Action } from "@/lib/api/client";

const FIELD =
  "type-input mt-1.5 w-full rounded-md border border-warm-400 bg-warm-50 px-3 py-2 outline-none focus:border-orange focus:ring-2 focus:ring-orange/30";

/** The wording is hers to change until she reports. After that the ledger keeps her word. */
export function Wording({ action }: { action: Action }) {
  const [editing, setEditing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [pending, startTransition] = useTransition();

  /** The editor closes on a saved wording and stays open on an error. */
  const save = (formData: FormData) =>
    startTransition(async () => {
      const state = await rewriteAction(formData);
      setError(state.error ?? null);
      if (state.ok) setEditing(false);
    });

  if (!editing) {
    return (
      <>
        <p className="type-body font-semibold">{action.text}</p>
        {action.why && <p className="type-body text-warm-500">{action.why}</p>}
        {action.status === "committed" && (
          <button
            type="button"
            onClick={() => setEditing(true)}
            className="type-label motion-fast mt-1 cursor-pointer text-burgundy hover:text-burgundy-hover"
          >
            Edit the wording
          </button>
        )}
      </>
    );
  }

  return (
    <form action={save} className="mt-1">
      <input type="hidden" name="action_id" value={action.id} />
      <label className="type-label block">
        What&apos;s the one thing you&apos;ll do before the next meeting?
        <textarea
          name="text"
          rows={2}
          required
          defaultValue={action.text}
          className={FIELD}
        />
      </label>
      <label className="type-label mt-3 block">
        Why it matters{" "}
        <span className="font-normal text-warm-500">(optional)</span>
        <input name="why" defaultValue={action.why ?? ""} className={FIELD} />
      </label>
      <div className="mt-4 flex items-center gap-3">
        <button
          type="submit"
          disabled={pending}
          className="btn btn-primary disabled:opacity-60"
        >
          {pending ? "Saving…" : "Save the wording"}
        </button>
        <button
          type="button"
          onClick={() => setEditing(false)}
          className="btn btn-ghost"
        >
          Cancel
        </button>
        {error && <span className="type-caption text-red">{error}</span>}
      </div>
    </form>
  );
}
