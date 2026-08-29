import type { ReactNode } from "react";
import { CircleHeader } from "@/components/circle/CircleHeader";
import { currentMember } from "@/lib/member";
import { CIRCLE_LEADER_ID, SEED_MEMBERS } from "@/lib/seed";

export default async function CircleLayout({ children }: { children: ReactNode }) {
  const member = await currentMember();
  return (
    <div className="pb-12">
      <CircleHeader
        name="West Coast Execs"
        memberCount={SEED_MEMBERS.length}
        youLead={member.id === CIRCLE_LEADER_ID}
      />
      {children}
    </div>
  );
}
