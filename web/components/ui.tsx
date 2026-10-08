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
