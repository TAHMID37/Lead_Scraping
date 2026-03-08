import type { Metadata } from "next";
import { DM_Sans, JetBrains_Mono } from "next/font/google";
import "./globals.css";
import { ApiKeysProvider } from "@/lib/api-keys";
import { ScrapeProvider } from "@/lib/scrape-context";
import { AppShell } from "@/components/layout/app-shell";
import { Toaster } from "sonner";

const dmSans = DM_Sans({
  subsets: ["latin"],
  variable: "--font-body",
});

const jetbrainsMono = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-heading",
});

export const metadata: Metadata = {
  title: "JobScraper // ANZSCO 482",
  description: "Australian job scraping with AI-powered ANZSCO 482 visa validation",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body className={`${dmSans.variable} ${jetbrainsMono.variable} ${dmSans.className}`}>
        <ApiKeysProvider>
          <ScrapeProvider>
          <AppShell>{children}</AppShell>
          <Toaster
            richColors
            position="top-right"
            toastOptions={{
              style: {
                background: "oklch(0.17 0.005 260)",
                border: "1px solid oklch(0.25 0.008 260)",
                color: "oklch(0.93 0.005 260)",
              },
            }}
          />
          </ScrapeProvider>
        </ApiKeysProvider>
      </body>
    </html>
  );
}
