"use server";

import { revalidatePath } from "next/cache";
import { cookies } from "next/headers";
import { api, ApiError } from "@/lib/api/client";
import { currentMember, MEMBER_COOKIE } from "@/lib/member";

export type FormState = { error?: string; ok?: boolean };

export async function switchMember(formData: FormData) {
  const id = String(formData.get("member_id") ?? "");
  (await cookies()).set(MEMBER_COOKIE, id, { path: "/", sameSite: "lax" });
  revalidatePath("/", "layout");
}

export async function recordAction(_: FormState, formData: FormData): Promise<FormState> {
  const member = await currentMember();
  const circleId = String(formData.get("circle_id"));
  const meetingId = String(formData.get("meeting_id"));
  const text = String(formData.get("text") ?? "").trim();
  const why = String(formData.get("why") ?? "").trim() || null;
  if (!text) return { error: "Say the one thing you'll do." };
  try {
    await api(`/circles/${circleId}/meetings/${meetingId}/actions`, member.id, {
      method: "POST",
      body: JSON.stringify({ text, why }),
    });
  } catch (e) {
    return { error: e instanceof ApiError ? e.message : "Something went wrong." };
  }
  revalidatePath("/", "layout");
  return { ok: true };
}

export async function reportAction(_: FormState, formData: FormData): Promise<FormState> {
  const member = await currentMember();
  const actionId = String(formData.get("action_id"));
  const status = String(formData.get("status"));
  const note = String(formData.get("note") ?? "").trim() || null;
  try {
    await api(`/actions/${actionId}`, member.id, {
      method: "PATCH",
      body: JSON.stringify({ status, note }),
    });
  } catch (e) {
    return { error: e instanceof ApiError ? e.message : "Something went wrong." };
  }
  revalidatePath("/", "layout");
  return { ok: true };
}
