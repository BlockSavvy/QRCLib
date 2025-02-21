import type { Metadata } from "next";
import { Inter } from "next/font/google";
import Link from "next/link";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "PQCL - Quantum-Resistant Cryptography Library",
  description: "A Python library implementing quantum-resistant cryptographic algorithms, including Kyber and Dilithium.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <nav>
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between h-16">
              <div className="flex">
                <div className="flex-shrink-0 flex items-center">
                  <Link href="/" className="text-xl font-bold neon-text">
                    PQCL
                  </Link>
                </div>
                <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
                  <Link href="/examples/basic" className="text-secondary hover:neon-text px-3 py-2 rounded-md text-sm font-medium">
                    Basic Examples
                  </Link>
                  <Link href="/examples/messaging" className="text-secondary hover:neon-text px-3 py-2 rounded-md text-sm font-medium">
                    Secure Messaging
                  </Link>
                  <Link href="/examples/blockchain" className="text-secondary hover:neon-text px-3 py-2 rounded-md text-sm font-medium">
                    Blockchain
                  </Link>
                  <Link href="/examples/bitcoin" className="text-secondary hover:neon-text px-3 py-2 rounded-md text-sm font-medium">
                    Bitcoin Protection
                  </Link>
                </div>
              </div>
              <div className="flex items-center">
                <a
                  href="https://github.com/BlockSavvy/QRCLib"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-secondary hover:neon-text"
                >
                  GitHub
                </a>
              </div>
            </div>
          </div>
        </nav>
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {children}
        </main>
      </body>
    </html>
  );
}
