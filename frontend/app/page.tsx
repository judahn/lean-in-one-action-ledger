import { redirect } from "next/navigation";
import { SEED_CIRCLE_ID } from "@/lib/seed";

export default function Home() {
  redirect(`/circles/${SEED_CIRCLE_ID}/one-action`);
}
