import { Bell, Menu, Search, Sparkles } from "lucide-react";
import type { Member } from "@/lib/member";
import { Logo } from "./Logo";
import { MemberSwitcher } from "./MemberSwitcher";

/** Connect's bar. On a phone it collapses the way Connect's does: hamburger, wordmark, icons. */
export function TopBar({ member }: { member: Member }) {
  return (
    <header className="flex h-16 items-center gap-2 border-b border-warm-300 bg-warm-50 px-3 sm:gap-3 sm:px-4 md:gap-6 md:px-6">
      <span className="flex size-8 shrink-0 items-center justify-center lg:hidden">
        <Menu className="size-5" strokeWidth={1.75} />
      </span>
      <Logo className="h-[15px] w-auto shrink-0 text-warm-900 sm:h-[18px]" />
      <div className="surface relative hidden h-9 w-full max-w-[460px] items-center rounded-full pr-3 pl-[38px] text-warm-500 md:flex">
        <Search className="absolute left-3 size-4" />
        <span className="type-body flex-1 truncate">Search topics, members, guides, Circles and more</span>
        <span className="type-label-sm ml-2">⌘K</span>
      </div>
      <div className="ml-auto flex shrink-0 items-center gap-1 text-warm-900">
        <span className="flex size-9 items-center justify-center md:hidden">
          <Search className="size-5" strokeWidth={1.75} />
        </span>
        <span className="hidden size-9 items-center justify-center sm:flex">
          <Sparkles className="size-5" strokeWidth={1.75} />
        </span>
        <span className="relative flex size-9 items-center justify-center">
          <Bell className="size-5" strokeWidth={1.75} />
          <span className="type-label-sm absolute top-0.5 right-0.5 flex h-[18px] min-w-[18px] items-center justify-center rounded-full bg-red px-[5px] text-warm-100">
            1
          </span>
        </span>
        <span className="mx-2 hidden h-6 w-px bg-warm-300 sm:block" />
        <MemberSwitcher member={member} />
      </div>
    </header>
  );
}
