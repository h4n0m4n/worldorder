import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "WORLD ORDER — AI Geopolitical Simulation",
  description:
    "AI-Powered Civilization & Geopolitical Simulation Engine. Real leaders. Real decisions. Simulated futures.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <head>
        <link
          href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="min-h-screen antialiased">{children}</body>
    </html>
  );
}
