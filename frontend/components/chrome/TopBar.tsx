import { Bell, Search, Sparkles } from "lucide-react";
import type { Member } from "@/lib/member";
import { MemberSwitcher } from "./MemberSwitcher";

export function TopBar({ member }: { member: Member }) {
  return (
    <header className="flex h-16 items-center gap-6 border-b border-warm-300 bg-warm-50 px-6">
      <div className="shrink-0 text-[15px] font-bold tracking-[0.2em] text-warm-900">
        LEAN <span className="border-b-2 border-burgundy pb-px">IN</span> CONNECT
      </div>
      <div className="surface relative flex h-9 w-full max-w-[460px] items-center rounded-full pr-3 pl-[38px] text-warm-500">
        <Search className="absolute left-3 size-4" />
        <span className="type-body flex-1 truncate">Search topics, members, guides, Circles and more</span>
        <span className="type-label-sm ml-2">⌘K</span>
      </div>
      <div className="ml-auto flex shrink-0 items-center gap-1 text-warm-900">
        <span className="flex size-9 items-center justify-center">
          <Sparkles className="size-5" strokeWidth={1.75} />
        </span>
        <span className="relative flex size-9 items-center justify-center">
          <Bell className="size-5" strokeWidth={1.75} />
          <span className="type-label-sm absolute top-0.5 right-0.5 flex h-[18px] min-w-[18px] items-center justify-center rounded-full bg-red px-[5px] text-warm-100">
            1
          </span>
        </span>
        <span className="mx-2 h-6 w-px bg-warm-300" />
        <MemberSwitcher member={member} />
      </div>
    </header>
  );
}
