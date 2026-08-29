import type { CheckIn } from "@/lib/api/client";

/** Counts first. The rate is there, quietly, because a Circle is not a scoreboard. */
export function FollowThrough({ ft }: { ft: CheckIn["follow_through"] }) {
  const tiles = [
    { label: "Done", n: ft.done, dot: "bg-emerald" },
    { label: "Partly", n: ft.partly, dot: "bg-orange" },
    { label: "Not yet", n: ft.not_yet, dot: "bg-burgundy" },
    { label: "Not reported", n: ft.open, dot: "bg-warm-400" },
  ];
  const span = ft.window_meetings === 1 ? "the last meeting" : `the last ${ft.window_meetings} meetings`;
  return (
    <div className="flex flex-wrap items-end gap-x-6 gap-y-3 rounded-md bg-warm-200 px-5 py-4">
      {tiles.map((t) => (
        <div key={t.label}>
          <div className="type-numeric">{t.n}</div>
          <div className="type-caption mt-1 flex items-center gap-1.5 text-warm-500">
            <span className={`size-2 rounded-full ${t.dot}`} /> {t.label}
          </div>
        </div>
      ))}
      <div className="type-caption ml-auto text-right text-warm-500">
        {ft.committed} actions over {span}
        {ft.rate !== null && (
          <div className="mt-0.5">
            <span className="font-semibold text-warm-900">{Math.round(ft.rate * 100)}%</span> follow-through
          </div>
        )}
      </div>
    </div>
  );
}
