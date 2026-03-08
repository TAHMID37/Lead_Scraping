"use client";

import { useEffect, useState, useRef } from "react";
import { useApi } from "@/hooks/use-api";
import Link from "next/link";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Radar,
  Briefcase,
  CheckCircle2,
  Building2,
  ArrowRight,
  TrendingUp,
} from "lucide-react";
import type { DashboardStats, ScrapeSession } from "@/lib/types";

export default function DashboardPage() {
  const api = useApi();
  const apiRef = useRef(api);
  apiRef.current = api;
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [sessions, setSessions] = useState<ScrapeSession[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const [statsRes, sessionsRes] = await Promise.allSettled([
          apiRef.current.get("/api/stats"),
          apiRef.current.get("/api/sessions", { params: { limit: 5 } }),
        ]);
        if (statsRes.status === "fulfilled") setStats(statsRes.value.data);
        if (sessionsRes.status === "fulfilled") setSessions(sessionsRes.value.data.sessions || []);
      } catch {
        // silently handle
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  const statCards = [
    {
      label: "Total Sessions",
      value: stats?.total_sessions ?? 0,
      icon: Radar,
      color: "text-primary",
      bg: "bg-primary/10",
    },
    {
      label: "Jobs Scraped",
      value: stats?.total_jobs ?? 0,
      icon: Briefcase,
      color: "text-blue-400",
      bg: "bg-blue-500/10",
    },
    {
      label: "ANZSCO Eligible",
      value: stats?.eligible_jobs ?? 0,
      icon: CheckCircle2,
      color: "text-emerald-400",
      bg: "bg-emerald-500/10",
      subtext: stats?.total_jobs ? `${((stats?.eligible_jobs ?? 0) / stats.total_jobs * 100).toFixed(0)}% rate` : undefined,
    },
    {
      label: "Companies",
      value: stats?.total_companies ?? 0,
      icon: Building2,
      color: "text-amber-400",
      bg: "bg-amber-500/10",
    },
  ];

  function formatDate(dateStr: string) {
    return new Date(dateStr).toLocaleDateString("en-AU", {
      day: "numeric",
      month: "short",
      hour: "2-digit",
      minute: "2-digit",
    });
  }

  function platformBadge(platform: string) {
    const styles: Record<string, string> = {
      indeed: "bg-blue-500/10 text-blue-400 border-blue-500/20",
      seek: "bg-purple-500/10 text-purple-400 border-purple-500/20",
      careerone: "bg-amber-500/10 text-amber-400 border-amber-500/20",
    };
    return (
      <Badge variant="outline" className={styles[platform] || ""}>
        {platform}
      </Badge>
    );
  }

  function statusBadge(status: string) {
    const styles: Record<string, string> = {
      completed: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
      failed: "bg-red-500/10 text-red-400 border-red-500/20",
      scraping: "bg-primary/10 text-primary border-primary/20",
      validating: "bg-amber-500/10 text-amber-400 border-amber-500/20",
    };
    return (
      <Badge variant="outline" className={styles[status] || "bg-muted text-muted-foreground"}>
        {status}
      </Badge>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-end justify-between">
        <div>
          <h1 className="font-[family-name:var(--font-heading)] text-2xl font-bold tracking-tight">
            Dashboard
          </h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Overview of your scraping activity
          </p>
        </div>
        <Link href="/scrape">
          <Button size="sm" className="gap-2 font-[family-name:var(--font-heading)] text-xs font-semibold tracking-wide">
            <Radar className="size-3.5" />
            New Scrape
          </Button>
        </Link>
      </div>

      {/* Stat Cards */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {statCards.map((card) => (
          <Card key={card.label} className="border-border/50 bg-card/50 backdrop-blur-sm">
            <CardContent className="pt-5">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-xs font-medium uppercase tracking-wider text-muted-foreground">
                    {card.label}
                  </p>
                  {loading ? (
                    <Skeleton className="mt-2 h-8 w-20" />
                  ) : (
                    <p className="mt-1 font-[family-name:var(--font-heading)] text-3xl font-bold tabular-nums">
                      {card.value.toLocaleString()}
                    </p>
                  )}
                  {card.subtext && !loading && (
                    <div className="mt-1 flex items-center gap-1 text-xs text-emerald-400">
                      <TrendingUp className="size-3" />
                      {card.subtext}
                    </div>
                  )}
                </div>
                <div className={`rounded-lg p-2.5 ${card.bg}`}>
                  <card.icon className={`size-4 ${card.color}`} />
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Recent Sessions */}
      <Card className="border-border/50 bg-card/50">
        <CardHeader className="flex-row items-center justify-between border-b border-border/50 pb-4">
          <CardTitle className="font-[family-name:var(--font-heading)] text-sm font-semibold tracking-wide">
            Recent Sessions
          </CardTitle>
          <Link href="/history">
            <Button variant="ghost" size="sm" className="gap-1 text-xs text-muted-foreground hover:text-foreground">
              View All
              <ArrowRight className="size-3" />
            </Button>
          </Link>
        </CardHeader>
        <CardContent className="p-0">
          {loading ? (
            <div className="space-y-0 divide-y divide-border/50">
              {Array.from({ length: 3 }).map((_, i) => (
                <div key={i} className="px-6 py-4">
                  <Skeleton className="h-5 w-full" />
                </div>
              ))}
            </div>
          ) : sessions.length === 0 ? (
            <div className="py-12 text-center">
              <Radar className="mx-auto mb-3 size-8 text-muted-foreground/40" />
              <p className="text-sm text-muted-foreground">No sessions yet</p>
              <Link href="/scrape">
                <Button variant="outline" size="sm" className="mt-3 text-xs">
                  Start Scraping
                </Button>
              </Link>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow className="border-border/50 hover:bg-transparent">
                  <TableHead className="text-xs font-medium uppercase tracking-wider text-muted-foreground">Platform</TableHead>
                  <TableHead className="text-xs font-medium uppercase tracking-wider text-muted-foreground">Job Titles</TableHead>
                  <TableHead className="text-xs font-medium uppercase tracking-wider text-muted-foreground">Location</TableHead>
                  <TableHead className="text-xs font-medium uppercase tracking-wider text-muted-foreground">Status</TableHead>
                  <TableHead className="text-xs font-medium uppercase tracking-wider text-muted-foreground text-right">Jobs</TableHead>
                  <TableHead className="text-xs font-medium uppercase tracking-wider text-muted-foreground">Date</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {sessions.map((session) => (
                  <TableRow key={session.id} className="border-border/50 hover:bg-accent/50 cursor-pointer" onClick={() => window.location.href = `/history/${session.id}`}>
                    <TableCell>{platformBadge(session.platform)}</TableCell>
                    <TableCell className="max-w-[200px] truncate text-sm">
                      {session.job_titles.join(", ")}
                    </TableCell>
                    <TableCell className="text-sm text-muted-foreground">{session.location}</TableCell>
                    <TableCell>{statusBadge(session.status)}</TableCell>
                    <TableCell className="text-right font-[family-name:var(--font-heading)] text-sm tabular-nums">{session.total_jobs}</TableCell>
                    <TableCell className="text-xs text-muted-foreground">{formatDate(session.created_at)}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
