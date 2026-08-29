// The seed Circle meets on the West Coast. A real Circle carries its own timezone.
export const CIRCLE_TZ = "America/Los_Angeles";

export function meetingDay(iso: string, style: "long" | "short" = "long"): string {
  const date = new Date(iso);
  return new Intl.DateTimeFormat("en-US", {
    timeZone: CIRCLE_TZ,
    weekday: style === "long" ? "long" : undefined,
    month: style === "long" ? "long" : "short",
    day: "numeric",
  }).format(date);
}

export function meetingMonth(iso: string): string {
  return new Intl.DateTimeFormat("en-US", { timeZone: CIRCLE_TZ, month: "long" }).format(
    new Date(iso),
  );
}

export const STATUS_LABEL = {
  committed: "Not reported",
  done: "Done",
  partly: "Partly",
  not_yet: "Not yet",
} as const;

/** Avatar tones from Connect, assigned by member so a person keeps her color. */
const TONES = [
  ["#f3e8ee", "#6e1113"],
  ["#e8f0f7", "#1a3a5c"],
  ["#e8f5ee", "#1a5c3a"],
  ["#f5f0e8", "#5c3a1a"],
  ["#eeedf8", "#3a1a5c"],
  ["#f0f8ee", "#1a5c1a"],
  ["#fbecd8", "#6c3a05"],
  ["#f7e8ec", "#5c1a30"],
] as const;

export function toneFor(id: string): { bg: string; fg: string } {
  const n = parseInt(id.slice(-2), 16) || 0;
  const [bg, fg] = TONES[n % TONES.length];
  return { bg, fg };
}
