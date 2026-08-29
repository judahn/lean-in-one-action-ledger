import { Check } from "lucide-react";
import type { ActionStatus } from "@/lib/api/client";
import { STATUS_LABEL } from "@/lib/format";

const STYLE: Record<ActionStatus, string> = {
  done: "border-emerald/25 bg-tint-green text-emerald",
  partly: "border-[#6c3a05]/25 bg-tint-orange text-[#6c3a05]",
  not_yet: "border-burgundy/25 bg-tint-poppy text-burgundy",
  committed: "border-warm-400/60 bg-warm-200 text-warm-500",
};

export function StatusPill({ status }: { status: ActionStatus }) {
  return (
    <span
      className={`type-label-sm inline-flex h-5 shrink-0 items-center gap-1.5 rounded-full border px-[9px] whitespace-nowrap ${STYLE[status]}`}
    >
      {status === "done" && <Check className="size-3" strokeWidth={2} />}
      {STATUS_LABEL[status]}
    </span>
  );
}
