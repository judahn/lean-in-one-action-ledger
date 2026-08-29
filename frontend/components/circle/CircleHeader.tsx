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
    <span className="flex items-center gap-1">
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
      <div className="h-[270px] bg-gradient-to-br from-[#e6f1ea] via-[#cfe3d7] to-[#b3d0c0]" />
      <div className="surface mx-8 -mt-20 p-6">
        <div className="flex items-start justify-between gap-4">
          <div className="flex flex-col gap-3">
            <h1 className="type-title">{name}</h1>
            <div className="type-caption flex items-center gap-3 text-warm-500">
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
          <div className="flex items-center gap-3">
            <span className="flex size-9 items-center justify-center rounded-full border border-warm-300">
              <Pin className="size-4" strokeWidth={1.75} />
            </span>
            <span className="type-label flex h-9 items-center gap-2 px-4">
              <Sparkles className="size-4" strokeWidth={1.75} /> Circle Leader
              tips
            </span>
            <span className="type-label flex h-9 items-center gap-2 rounded-full bg-burgundy px-4 text-warm-100">
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
    <div className="type-label flex items-center gap-1 py-3">
      {TABS.map((tab) => (
        <span key={tab} className="flex h-9 items-center px-3 text-warm-500">
          {tab}
        </span>
      ))}
      <Link
        href={`/circles/${circleId}/one-action`}
        className="flex h-9 items-center rounded-full bg-warm-900 px-3 text-warm-100"
      >
        One Action
      </Link>
    </div>
  );
}
