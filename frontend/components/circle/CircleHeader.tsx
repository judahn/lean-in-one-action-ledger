import { Calendar, Pin, Settings, Sparkles, Users, Video } from "lucide-react";
import Link from "next/link";

const TABS = ["Overview", "Feed", "Members", "Events", "Resources"];

function Meta({
  icon: Icon,
  children,
}: {
  icon: typeof Calendar;
  children: React.ReactNode;
}) {
  return (
    <span className="flex items-center gap-1 whitespace-nowrap">
      <Icon className="size-3.5" /> {children}
    </span>
  );
}

export function CircleHeader({
  name,
  memberCount,
  youLead,
}: {
  name: string;
  memberCount: number;
  youLead: boolean;
}) {
  return (
    <>
      <div className="h-40 bg-gradient-to-br from-[#e6f1ea] via-[#cfe3d7] to-[#b3d0c0] sm:h-[270px]" />
      <div className="surface mx-4 -mt-16 p-5 sm:mx-8 sm:-mt-20 sm:p-6">
        {/* On a phone the actions drop under the title and center, as they do on Connect. */}
        <div className="flex flex-col gap-5 sm:flex-row sm:items-start sm:justify-between sm:gap-4">
          <div className="flex flex-col gap-3">
            <h1 className="type-title">{name}</h1>
            <div className="type-caption flex flex-wrap items-center gap-x-3 gap-y-1 text-warm-500">
              <Meta icon={Calendar}>Started Jun 2026</Meta>
              <span className="size-[3px] rounded-full bg-warm-400" />
              <Meta icon={Video}>Virtual</Meta>
              <span className="size-[3px] rounded-full bg-warm-400" />
              <Meta icon={Users}>{memberCount} members</Meta>
            </div>
            {youLead && (
              <span className="type-label-sm inline-flex h-5 w-fit items-center gap-1.5 rounded-full border border-burgundy/25 bg-tint-poppy px-[9px] text-burgundy">
                <Sparkles className="size-3" /> You lead this Circle
              </span>
            )}
          </div>
          <div className="flex items-center justify-center gap-3 sm:justify-end">
            <span className="hidden size-9 items-center justify-center rounded-full border border-warm-300 sm:flex">
              <Pin className="size-4" strokeWidth={1.75} />
            </span>
            <span className="type-label flex h-9 items-center gap-2 px-3 whitespace-nowrap sm:px-4">
              <Sparkles className="size-4" strokeWidth={1.75} /> Circle Leader tips
            </span>
            <span className="type-label flex h-9 items-center gap-2 rounded-full bg-burgundy px-4 whitespace-nowrap text-warm-100">
              <Settings className="size-4" /> Manage
            </span>
          </div>
        </div>
      </div>
    </>
  );
}

export function CircleTabs({ circleId }: { circleId: string }) {
  return (
    <div className="type-label flex items-center gap-1 overflow-x-auto py-3 whitespace-nowrap">
      {TABS.map((tab, i) => (
        <span
          key={tab}
          className={`h-9 shrink-0 items-center px-3 text-warm-500 ${i >= 3 ? "hidden sm:flex" : "flex"}`}
        >
          {tab}
        </span>
      ))}
      <Link
        href={`/circles/${circleId}/one-action`}
        className="flex h-9 shrink-0 items-center rounded-full bg-warm-900 px-3 text-warm-100"
      >
        One Action
      </Link>
    </div>
  );
}
