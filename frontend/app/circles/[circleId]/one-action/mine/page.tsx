import { CircleTabs } from "@/components/circle/CircleHeader";
import { SubNav } from "@/components/circle/SubNav";
import { RecordForm } from "@/components/one-action/RecordForm";
import { ReportForm } from "@/components/one-action/ReportForm";
import { StatusPill } from "@/components/one-action/StatusPill";
import { checkIn, myActions } from "@/lib/api/client";
import { meetingDay } from "@/lib/format";
import { currentMember } from "@/lib/member";
import { DEMO_AS_OF } from "@/lib/seed";

export default async function MyActionsPage({
  params,
}: {
  params: Promise<{ circleId: string }>;
}) {
  const { circleId } = await params;
  const member = await currentMember();
  const [update, actions] = await Promise.all([
    checkIn(circleId, member.id, DEMO_AS_OF),
    myActions(member.id),
  ]);
  const next = update.next_meeting;
  const forNext = actions.find((a) => a.meeting_id === next.id);
  const open = actions.filter(
    (a) => a.meeting_id !== next.id && a.status !== "done",
  );
  const history = actions.filter((a) => a.meeting_id !== next.id);
  const heldAt = (meetingId: string) =>
    meetingId === update.since_meeting?.id
      ? update.since_meeting.held_at
      : update.actions.find((a) => a.committed_at.id === meetingId)
          ?.committed_at.held_at;
  const when = (meetingId: string, prefix = "") => {
    const at = heldAt(meetingId);
    return at ? `${prefix}${meetingDay(at, "short")}` : prefix.trim();
  };

  return (
    <div className="mx-8 grid grid-cols-1 gap-x-6 xl:grid-cols-[1fr_320px]">
      <div className="flex flex-col gap-3">
        <CircleTabs circleId={circleId} />
        <section className="surface flex flex-col gap-6 p-6">
          <div className="flex flex-wrap items-start justify-between gap-3">
            <div>
              <h2 className="type-title">My One Actions</h2>
              <p className="type-caption mt-1 text-warm-500">
                Only you see this page.
              </p>
            </div>
            <SubNav circleId={circleId} active="mine" />
          </div>

          <div>
            <h3 className="type-overline text-burgundy">
              For {meetingDay(next.held_at)}
            </h3>
            {forNext ? (
              <div className="mt-3 rounded-lg border border-warm-300 p-4">
                <div className="type-caption text-warm-500">
                  Committed for {meetingDay(next.held_at, "short")}. Report on
                  it whenever it lands.
                </div>
                <p className="type-body font-semibold">{forNext.text}</p>
                {forNext.why && (
                  <p className="type-body text-warm-500">{forNext.why}</p>
                )}
                <ReportForm action={forNext} />
              </div>
            ) : (
              <RecordForm circleId={circleId} meetingId={next.id} />
            )}
          </div>

          {open.length > 0 && (
            <div>
              <h3 className="type-overline text-burgundy">How did it go?</h3>
              <ul className="mt-3 flex flex-col gap-3">
                {open.map((a) => (
                  <li
                    key={a.id}
                    className="rounded-lg border border-warm-300 p-4"
                  >
                    <div className="type-caption text-warm-500">
                      {when(a.meeting_id, "Committed ")}
                    </div>
                    <p className="type-body font-semibold">{a.text}</p>
                    <ReportForm action={a} />
                  </li>
                ))}
              </ul>
            </div>
          )}

          <div>
            <h3 className="type-overline text-burgundy">History</h3>
            <ul className="mt-1 divide-y divide-warm-200">
              {history.map((a) => (
                <li key={a.id} className="flex items-start gap-3 py-3">
                  <div className="min-w-0 flex-1">
                    <div className="type-caption text-warm-500">
                      {when(a.meeting_id)}
                    </div>
                    <div className="type-body font-semibold">{a.text}</div>
                    {a.note && (
                      <div className="type-body text-warm-500">{a.note}</div>
                    )}
                  </div>
                  <StatusPill status={a.status} />
                </li>
              ))}
            </ul>
          </div>
        </section>
      </div>

      <aside className="xl:pt-3">
        <section className="surface p-6">
          <h3 className="type-overline text-burgundy">The One Action</h3>
          <p className="type-title-sm mt-3">
            The little push you need to go for it.
          </p>
          <p className="type-body mt-2 text-warm-500">
            One concrete thing you&apos;ll do before the next meeting. Small
            enough to finish, real enough to matter. The Circle opens its next
            meeting with everyone&apos;s update.
          </p>
        </section>
      </aside>
    </div>
  );
}
