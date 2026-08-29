import { toneFor } from "@/lib/format";

export function Avatar({
  id,
  name,
  size = 40,
}: {
  id: string;
  name: string;
  size?: number;
}) {
  const tone = toneFor(id);
  return (
    <span
      className="flex shrink-0 items-center justify-center rounded-full font-serif font-semibold"
      style={{
        background: tone.bg,
        color: tone.fg,
        width: size,
        height: size,
        fontSize: size * 0.36,
      }}
    >
      {name.slice(0, 2).toUpperCase()}
    </span>
  );
}
