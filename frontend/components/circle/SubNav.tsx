import Link from "next/link";

/** The two moments of the ritual: the Circle's Update, and your own actions. */
export function SubNav({ circleId, active }: { circleId: string; active: "update" | "mine" }) {
  const base = `/circles/${circleId}/one-action`;
  const item = (href: string, label: string, isActive: boolean) => (
    <Link
      href={href}
      className={`type-label flex h-8 items-center rounded-full px-3 transition-colors ${
        isActive ? "bg-tint-poppy text-burgundy" : "text-warm-500 hover:bg-warm-200"
      }`}
    >
      {label}
    </Link>
  );
  return (
    <div className="flex items-center gap-1">
      {item(base, "Circle update", active === "update")}
      {item(`${base}/mine`, "My actions", active === "mine")}
    </div>
  );
}
