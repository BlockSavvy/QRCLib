"use client";

import type { ReactNode } from "react";

export function Panel({
  eyebrow,
  title,
  children,
}: {
  eyebrow?: string;
  title: string;
  children: ReactNode;
}) {
  return (
    <section className="border border-line bg-panel p-4 sm:p-5">
      {eyebrow ? <p className="font-mono text-[11px] tracking-wide text-brass">{eyebrow}</p> : null}
      <h2 className="mt-1 text-lg font-medium">{title}</h2>
      <div className="mt-4 space-y-3">{children}</div>
    </section>
  );
}

export function Note({ children }: { children: ReactNode }) {
  return <p className="text-sm leading-relaxed text-muted">{children}</p>;
}

export function Reading({ children }: { children: ReactNode }) {
  return <p className="border-l-2 border-brass pl-3 text-sm leading-relaxed text-paper">{children}</p>;
}

export function Steps({ items }: { items: { title: string; body: string }[] }) {
  return (
    <ol className="space-y-3">
      {items.map((item, index) => (
        <li key={item.title} className="flex gap-3">
          <span className="mt-0.5 font-mono text-xs text-brass">{String(index + 1).padStart(2, "0")}</span>
          <div>
            <p className="text-sm text-paper">{item.title}</p>
            <p className="mt-1 text-sm leading-relaxed text-muted">{item.body}</p>
          </div>
        </li>
      ))}
    </ol>
  );
}

export function Python({ source }: { source: string }) {
  return (
    <details className="border border-line bg-ink">
      <summary className="cursor-pointer px-3 py-3 text-sm text-muted">Same call in Python</summary>
      <pre className="overflow-x-auto px-3 pb-3 font-mono text-xs leading-relaxed text-brass-2">{source}</pre>
    </details>
  );
}

export function Action({
  children,
  onClick,
  disabled,
  quiet,
}: {
  children: ReactNode;
  onClick: () => void;
  disabled?: boolean;
  quiet?: boolean;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={disabled}
      className={
        quiet
          ? "min-h-11 border border-line bg-ink px-4 py-2 text-sm text-paper"
          : "min-h-11 border border-brass bg-brass px-4 py-2 text-sm text-ink"
      }
    >
      {children}
    </button>
  );
}
