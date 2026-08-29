import type { components } from "./types";

export type CheckIn = components["schemas"]["CheckInResponse"];
export type CheckInAction = components["schemas"]["CheckInActionOut"];
export type Action = components["schemas"]["ActionResponse"];
export type ActionStatus = components["schemas"]["ActionStatus"];

const API = process.env.API_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  constructor(
    public status: number,
    detail: string,
  ) {
    super(detail);
  }
}

/** One thin call. The member header is the whole identity story for the take-home. */
export async function api<T>(path: string, memberId: string, init: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      "X-Member-Id": memberId,
      ...(init.headers ?? {}),
    },
    cache: "no-store",
  });
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new ApiError(response.status, body.detail ?? response.statusText);
  }
  return response.json() as Promise<T>;
}

export function checkIn(circleId: string, memberId: string, asOf: string) {
  const query = new URLSearchParams({ as_of: asOf });
  return api<CheckIn>(`/circles/${circleId}/meetings/next/check-in?${query}`, memberId);
}

export function myActions(memberId: string) {
  return api<Action[]>(`/members/${memberId}/actions`, memberId);
}
