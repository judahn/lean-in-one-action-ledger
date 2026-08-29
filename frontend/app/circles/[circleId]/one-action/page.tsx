import { MessageCircle } from "lucide-react";
import Link from "next/link";
import { CircleTabs } from "@/components/circle/CircleHeader";
import { SubNav } from "@/components/circle/SubNav";
import { Avatar } from "@/components/one-action/Avatar";
import { FollowThrough } from "@/components/one-action/FollowThrough";
import { Opener } from "@/components/one-action/Opener";
import { StatusPill } from "@/components/one-action/StatusPill";
import { UpdateList } from "@/components/one-action/UpdateList";
import { checkIn, myActions } from "@/lib/api/client";
import { meetingDay, meetingMonth } from "@/lib/format";
import { currentMember } from "@/lib/member";
import { CIRCLE_LEADER_ID, DEMO_AS_OF, SEED_MEMBERS } from "@/lib/seed";

export default async function OneActionUpdatePage({
  params,
}: {
  params: Promise<{ circleId: string }>;
}) {
  const { circleId } = await params;
  const member = await currentMember();
  const [update, own] = await Promise.all([
    checkIn(circleId, member.id, DEMO_AS_OF),
    myActions(member.id),
  ]);
  const mine = update.actions.find(
    (a) => a.member.id === member.id && !a.carried_over,
  );
  const upcoming = own.find((a) => a.meeting_id === update.next_meeting.id);
  const nextMonth = new Date(update.next_meeting.held_at);
  nextMonth.setMonth(nextMonth.getMonth() + 1);
  const base = `/circles/${circleId}/one-action`;

  return (
    <div className="mx-8 grid grid-cols-1 gap-x-6 xl:grid-cols-[1fr_320px]">
      <div className="flex flex-col gap-3">
        <CircleTabs circleId={circleId} />
        <section className="surface flex flex-col gap-4 p-6">
          <div className="flex flex-wrap items-start justify-between gap-3">
            <div>
              <h2 className="type-title">One Action Update</h2>
              <p className="type-caption mt-1 text-warm-500">
                For {meetingDay(update.next_meeting.held_at)}
                {update.next_meeting.moderator &&
                  ` · ${update.next_meeting.moderator.display_name} moderates`}
                {update.since_meeting &&
                  ` · Since ${meetingDay(update.since_meeting.held_at, "short")}`}
              </p>
            </div>
            <SubNav circleId={circleId} active="update" />
          </div>
          <FollowThrough ft={update.follow_through} />
          <Opener line={update.opener} source={update.opener_source} />
          <UpdateList
            actions={update.actions}
            sinceHeldAt={update.since_meeting?.held_at ?? null}
          />
        </section>
      </div>

      <aside className="flex flex-col gap-6 xl:pt-3">
        <section className="surface p-6">
          <h3 className="type-overline text-burgundy">Your One Action</h3>
          {upcoming && (
            <div className="mt-3 mb-4 border-b border-warm-200 pb-4">
              <div className="type-caption text-warm-500">
                Committed for {meetingDay(update.next_meeting.held_at, "short")}{" "}
                · reads out at the {meetingMonth(nextMonth.toISOString())}{" "}
                update
              </div>
              <p className="type-body font-semibold">{upcoming.text}</p>
              <div className="mt-2 flex items-center justify-between">
                <StatusPill status={upcoming.status} />
                <Link
                  href={`${base}/mine`}
                  className="type-label text-burgundy"
                >
                  Update it →
                </Link>
              </div>
            </div>
          )}
          {mine ? (
            <div className="mt-3">
              {update.since_meeting && (
                <div className="type-caption text-warm-500">
                  From {meetingDay(update.since_meeting.held_at, "short")}
                </div>
              )}
              <p className="type-body font-semibold">{mine.text}</p>
              {mine.note && (
                <p className="type-body text-warm-500">{mine.note}</p>
              )}
              <div className="mt-3 flex items-center justify-between">
                <StatusPill status={mine.status} />
                <Link
                  href={`${base}/mine`}
                  className="type-label text-burgundy"
                >
                  Update it →
                </Link>
              </div>
            </div>
          ) : (
            <div className="mt-3">
              <p className="type-body text-warm-500">
                Nothing on the ledger from the last meeting.
              </p>
              <Link
                href={`${base}/mine`}
                className="type-label mt-3 inline-block text-burgundy"
              >
                Record your One Action →
              </Link>
            </div>
          )}
        </section>

        <section className="surface p-6">
          <h3 className="type-overline text-burgundy">
            Members ({SEED_MEMBERS.length})
          </h3>
          <ul className="mt-4 flex flex-col gap-3">
            {SEED_MEMBERS.map((m) => (
              <li key={m.id} className="flex items-center gap-3">
                <Avatar id={m.id} name={m.name} size={32} />
                <span className="type-body">{m.name}</span>
                {m.id === CIRCLE_LEADER_ID && (
                  <span className="type-caption text-warm-500">Leader</span>
                )}
                {m.id === member.id && (
                  <span className="type-caption ml-auto text-warm-500">
                    you
                  </span>
                )}
              </li>
            ))}
          </ul>
          <span className="type-label-sm mt-4 flex h-7 items-center justify-center gap-2 rounded-full bg-warm-300">
            <MessageCircle className="size-4" strokeWidth={1.75} /> Start group
            chat
          </span>
        </section>
      </aside>
    </div>
  );
}
