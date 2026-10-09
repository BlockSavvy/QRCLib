"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const links = [
  ["/", "Start"],
  ["/exchange", "Exchange"],
  ["/sign", "Sign"],
  ["/messages", "Mail"],
  ["/bitcoin", "Bitcoin"],
  ["/envelope", "Envelope"],
];

export function Nav() {
  const path = usePathname();
  return (
    <header className="border-b border-line">
      <div className="mx-auto flex max-w-3xl flex-wrap items-center gap-x-4 gap-y-1 px-4 py-3">
        <Link href="/" className="py-2 text-sm font-medium tracking-wide text-brass-2">
          QRCLib
        </Link>
        <nav className="flex flex-wrap gap-x-1 text-sm">
          {links.map(([href, label]) => {
            const active = href === "/" ? path === "/" : path.startsWith(href);
            return (
              <Link
                key={href}
                href={href}
                aria-current={active ? "page" : undefined}
                className={
                  active
                    ? "min-h-11 border-b border-brass px-2 py-2 text-paper"
                    : "min-h-11 px-2 py-2 text-muted"
                }
              >
                {label}
              </Link>
            );
          })}
        </nav>
        <a href="https://github.com/BlockSavvy/QRCLib" className="ml-auto py-2 text-sm text-muted">
          GitHub
        </a>
      </div>
    </header>
  );
}
