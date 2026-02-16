import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });

export const metadata: Metadata = {
  title: "ModelAuditAI — ML Model Auditing System",
  description:
    "AI-powered machine learning model auditing. Detect bias, drift, overfitting, feature leakage, and get SHAP explainability with a single upload.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.variable} font-sans antialiased bg-zinc-950 text-zinc-100 min-h-screen`}>
        <nav className="border-b border-zinc-800/60 backdrop-blur-xl bg-zinc-950/80 sticky top-0 z-50">
          <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
            <a href="/" className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-violet-500 to-cyan-500 flex items-center justify-center">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  className="w-5 h-5 text-white"
                >
                  <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10" />
                  <path d="m9 12 2 2 4-4" />
                </svg>
              </div>
              <span className="text-lg font-bold tracking-tight">
                Model<span className="text-violet-400">Audit</span>AI
              </span>
            </a>
            <div className="flex items-center gap-4 text-sm text-zinc-400">
              <a href="/" className="hover:text-zinc-100 transition-colors">Home</a>
              <a
                href="https://github.com/sarthakpapneja/ML-Auditor"
                target="_blank"
                rel="noopener noreferrer"
                className="hover:text-zinc-100 transition-colors"
              >
                GitHub
              </a>
            </div>
          </div>
        </nav>
        <main>{children}</main>
      </body>
    </html>
  );
}
