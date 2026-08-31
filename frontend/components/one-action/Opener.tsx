export function Opener({ line }: { line: string }) {
  return (
    <blockquote className="rounded-lg bg-tint-poppy p-4">
      <div className="type-overline text-burgundy">Opener</div>
      <p className="mt-2 font-serif text-[18px] leading-[1.4] text-warm-900">
        {line}
      </p>
      <div className="type-caption mt-2 text-warm-500">
        Read it, or say it your way.
      </div>
    </blockquote>
  );
}
