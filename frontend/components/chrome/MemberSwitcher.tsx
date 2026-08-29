"use client";

import { ChevronDown } from "lucide-react";
import { switchMember } from "@/app/actions";
import { toneFor } from "@/lib/format";
import type { Member } from "@/lib/member";
import { SEED_MEMBERS } from "@/lib/seed";

/** Stands in for sign-in: pick who you are. The choice becomes the X-Member-Id header. */
export function MemberSwitcher({ member }: { member: Member }) {
  const tone = toneFor(member.id);
  return (
    <form action={switchMember} className="relative flex items-center gap-2 p-1" title="Switch member (demo)">
      <span
        className="flex size-9 items-center justify-center rounded-full font-serif text-[13px] font-semibold"
        style={{ background: tone.bg, color: tone.fg }}
      >
        {member.name.slice(0, 2).toUpperCase()}
      </span>
      <ChevronDown className="size-4 text-warm-500" />
      <select
        name="member_id"
        defaultValue={member.id}
        aria-label="Viewing as"
        className="absolute inset-0 cursor-pointer opacity-0"
        onChange={(e) => e.currentTarget.form?.requestSubmit()}
      >
        {SEED_MEMBERS.map((m) => (
          <option key={m.id} value={m.id}>
            {m.name}
          </option>
        ))}
      </select>
    </form>
  );
}
