import type { Metadata } from "next";
import { IBM_Plex_Mono, IBM_Plex_Sans } from "next/font/google";
import Link from "next/link";
import "./globals.css";

const sans = IBM_Plex_Sans({ subsets: ["latin"], weight: ["400", "500"], variable: "--font-sans" });
const mono = IBM_Plex_Mono({ subsets: ["latin"], weight: ["400"], variable: "--font-mono" });

export const metadata: Metadata = {
  title: "QRCLib",
  description: "ML-KEM, ML-DSA, X-Wing, and an optional CKKS envelope. Hybrid by default.",
};

const links = [
  ["/", "Bench"],
  ["/exchange", "Exchange"],
  ["/sign", "Sign"],
  ["/messages", "Mail"],
  ["/bitcoin", "Bitcoin"],
  ["/envelope", "Envelope"],
];

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className={`${sans.variable} ${mono.variable} font-sans`}>
        <header className="border-b border-line">
          <div className="mx-auto flex max-w-3xl flex-wrap items-center gap-x-4 gap-y-2 px-4 py-4">
            <Link href="/" className="text-sm font-medium tracking-wide text-brass-2">
              QRCLib
            </Link>
            <nav className="flex flex-wrap gap-x-3 gap-y-1 text-sm text-muted">
              {links.map(([href, label]) => (
                <Link key={href} href={href} className="min-h-11 py-2">
                  {label}
                </Link>
              ))}
            </nav>
            <a
              href="https://github.com/BlockSavvy/QRCLib"
              className="ml-auto text-sm text-muted"
            >
              GitHub
            </a>
          </div>
        </header>
        <main className="mx-auto max-w-3xl px-4 py-8">{children}</main>
      </body>
    </html>
  );
}
