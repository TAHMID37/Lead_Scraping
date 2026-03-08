"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useApiKeys } from "@/lib/api-keys";
import { useScrape } from "@/lib/scrape-context";
import {
  LayoutDashboard,
  Radar,
  History,
  Building2,
  Settings,
  Zap,
  Loader2,
} from "lucide-react";
import { cn } from "@/lib/utils";

const navItems = [
  { href: "/", label: "Dashboard", icon: LayoutDashboard },
  { href: "/scrape", label: "Scrape", icon: Radar },
  { href: "/history", label: "History", icon: History },
  { href: "/companies", label: "Companies", icon: Building2 },
  { href: "/settings", label: "Settings", icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();
  const { isConfigured } = useApiKeys();
  const { activeScrapes, hasActiveScrape } = useScrape();

  const runningScrapes = activeScrapes.filter(
    (s) => s.status === "scraping" || s.status === "validating" || s.status === "enriching"
  );

  return (
    <aside className="flex h-screen w-56 flex-col border-r border-border/50 bg-[oklch(0.12_0.005_260)]">
      {/* Logo */}
      <div className="flex items-center gap-2.5 border-b border-border/50 px-5 py-5">
        <div className="flex size-8 items-center justify-center rounded-md bg-primary/20 text-primary">
          <Zap className="size-4" />
        </div>
        <div>
          <h1 className="font-[family-name:var(--font-heading)] text-sm font-bold tracking-tight text-foreground">
            JobScraper
          </h1>
          <p className="font-[family-name:var(--font-heading)] text-[10px] tracking-widest text-primary/80">
            ANZSCO 482
          </p>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 space-y-1 px-3 py-4">
        {navItems.map((item) => {
          const isActive =
            item.href === "/"
              ? pathname === "/"
              : pathname.startsWith(item.href);
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "group flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-all duration-200",
                isActive
                  ? "bg-primary/10 text-primary shadow-[inset_0_0_0_1px_oklch(0.72_0.14_185/0.15)]"
                  : "text-muted-foreground hover:bg-accent hover:text-foreground"
              )}
            >
              <item.icon
                className={cn(
                  "size-4 shrink-0 transition-colors",
                  isActive ? "text-primary" : "text-muted-foreground group-hover:text-foreground"
                )}
              />
              {item.label}
            </Link>
          );
        })}
      </nav>

      {/* Active scrapes indicator */}
      {runningScrapes.length > 0 && (
        <div className="mx-3 mb-2 space-y-1.5">
          {runningScrapes.map((scrape) => (
            <Link
              key={scrape.sessionId}
              href="/scrape"
              className="flex items-center gap-2 rounded-lg bg-primary/10 border border-primary/20 px-3 py-2 text-xs transition-colors hover:bg-primary/15"
            >
              <Loader2 className="size-3 animate-spin text-primary shrink-0" />
              <div className="min-w-0 flex-1">
                <span className="block truncate font-medium text-primary capitalize">
                  {scrape.platform}
                </span>
                <span className="block truncate text-muted-foreground">
                  {scrape.status === "scraping" && "Scraping jobs..."}
                  {scrape.status === "validating" && "Validating ANZSCO..."}
                  {scrape.status === "enriching" && "Enriching companies..."}
                </span>
              </div>
            </Link>
          ))}
        </div>
      )}

      {/* Status */}
      <div className="border-t border-border/50 px-4 py-4">
        <div className="flex items-center gap-2 text-xs text-muted-foreground">
          <div
            className={cn(
              "size-2 rounded-full",
              isConfigured
                ? "bg-emerald-500 shadow-[0_0_6px_oklch(0.72_0.18_155)]"
                : "bg-red-500 shadow-[0_0_6px_oklch(0.55_0.2_25)]"
            )}
          />
          {isConfigured ? "Keys configured" : "Keys missing"}
        </div>
      </div>
    </aside>
  );
}
