import { cookies } from "next/headers";
import { SEED_MEMBERS } from "./seed";

export type Member = { id: string; name: string };

const COOKIE = "member_id";

/** Who is asking. A cookie set by the switcher, Priya by default. */
export async function currentMember(): Promise<Member> {
  const id = (await cookies()).get(COOKIE)?.value;
  return SEED_MEMBERS.find((m) => m.id === id) ?? SEED_MEMBERS[0];
}

export const MEMBER_COOKIE = COOKIE;
