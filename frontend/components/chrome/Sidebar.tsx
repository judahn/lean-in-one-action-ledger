import {
  BookOpen,
  Calendar,
  Home,
  MessageCircle,
  MessageSquare,
  Network,
  Users,
  UsersRound,
} from "lucide-react";
import type { ComponentType } from "react";

type Icon = ComponentType<{ className?: string; strokeWidth?: number }>;
type Item = { label: string; icon: Icon; active?: boolean };

const SECTIONS: { label: string; items: Item[] }[] = [
  { label: "Main", items: [{ label: "Home", icon: Home }] },
  {
    label: "Community",
    items: [
      { label: "Circles", icon: Users, active: true },
      { label: "Networks", icon: Network },
      { label: "Groups", icon: MessageCircle },
      { label: "People", icon: UsersRound },
    ],
  },
  {
    label: "Connect",
    items: [
      { label: "Messages", icon: MessageSquare },
      { label: "Events", icon: Calendar },
    ],
  },
  { label: "Learn", items: [{ label: "Resources", icon: BookOpen }] },
];

/** Connect's navigation, inert. Only the Circle it frames is real. */
export function Sidebar() {
  return (
    <nav className="hidden w-[188px] shrink-0 flex-col gap-6 bg-white border-r border-warm-300 pt-6 pr-2 pl-3 lg:sticky lg:top-16 lg:flex lg:h-[calc(100vh-4rem)] lg:self-start lg:overflow-y-auto">
      {SECTIONS.map((section) => (
        <div key={section.label} className="flex flex-col gap-1">
          <div className="type-overline mb-1 px-3 text-warm-500">
            {section.label}
          </div>
          {section.items.map(({ label, icon: Icon, active }) => (
            <div
              key={label}
              className={`type-body motion-fast flex cursor-pointer items-center gap-3 rounded-full px-3 py-2 ${
                active ? "bg-warm-300 font-bold" : "hover:bg-warm-200"
              }`}
            >
              <Icon
                className={`size-4 ${active ? "text-burgundy" : ""}`}
                strokeWidth={2.25}
              />
              {label}
            </div>
          ))}
        </div>
      ))}
    </nav>
  );
}
