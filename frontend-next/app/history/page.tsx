"use client";

import { useEffect, useState, useRef, useCallback } from "react";
import { useApi } from "@/hooks/use-api";
import Link from "next/link";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Calendar,
  MapPin,
  Briefcase,
  ChevronRight,
  SearchX,
  Zap,
} from "lucide-react";
import type { ScrapeSession, Platform } from "@/lib/types";

const PLATFORM_COLORS: Record<string, string> = {
  indeed: "bg-blue-500/15 text-blue-400 border-blue-500/25",
  seek: "bg-purple-500/15 text-purple-400 border-purple-500/25",
  careerone: "bg-amber-500/15 text-amber-400 border-amber-500/25",
};

const STATUS_COLORS: Record<string, string> = {
  completed: "bg-emerald-500/15 text-emerald-400 border-emerald-500/25",
  failed: "bg-red-500/15 text-red-400 border-red-500/25",
  scraping: "bg-cyan-500/15 text-cyan-400 border-cyan-500/25",
  validating: "bg-amber-500/15 text-amber-400 border-amber-500/25",
  running: "bg-cyan-500/15 text-cyan-400 border-cyan-500/25",
};

export default function HistoryPage() {
  const api = useApi();
  const apiRef = useRef(api);
  apiRef.current = api;
  const [sessions, setSessions] = useState<ScrapeSession[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<"all" | Platform>("all");
  const [page, setPage] = useState(1);
  const perPage = 10;

  useEffect(() => {
    async function fetchSessions() {
      setLoading(true);
      try {
        const params: Record<string, string | number> = { limit: 100 };
        if (filter !== "all") {
          params.platform = filter;
        }
        const res = await apiRef.current.get("/api/sessions", { params });
        const data = res.data;
        setSessions(data.sessions || []);
      } catch {
        setSessions([]);
      } finally {
        setLoading(false);
      }
    }
    fetchSessions();
  }, [filter]);

  const totalPages = Math.ceil(sessions.length / perPage);
  const paginated = sessions.slice((page - 1) * perPage, page * perPage);

  function formatDate(dateStr: string) {
    return new Date(dateStr).toLocaleDateString("en-AU", {
      day: "numeric",
      month: "short",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  }

  function truncateJobTitles(titles: string[], maxLen = 60): string {
    const joined = titles.join(", ");
    if (joined.length <= maxLen) return joined;
    return joined.slice(0, maxLen) + "...";
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="font-[family-name:var(--font-heading)] text-3xl font-bold tracking-tight">
          Scraping History
        </h1>
        <p className="mt-1 text-muted-foreground">
          Browse and review your past scraping sessions
        </p>
      </div>

      {/* Filter Tabs */}
      <Tabs
        value={filter}
        onValueChange={(v) => {
          setFilter(v as "all" | Platform);
          setPage(1);
        }}
      >
        <TabsList className="bg-secondary/50">
          <TabsTrigger value="all">All</TabsTrigger>
          <TabsTrigger value="indeed">Indeed</TabsTrigger>
          <TabsTrigger value="seek">Seek</TabsTrigger>
          <TabsTrigger value="careerone">CareerOne</TabsTrigger>
        </TabsList>
      </Tabs>

      {/* Content */}
      {loading ? (
        <div className="space-y-3">
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} className="h-28 w-full rounded-lg" />
          ))}
        </div>
      ) : paginated.length === 0 ? (
        <Card className="border-dashed">
          <CardContent className="flex flex-col items-center justify-center py-16 text-center">
            <div className="mb-4 rounded-full bg-muted p-4">
              <SearchX className="size-8 text-muted-foreground" />
            </div>
            <p className="text-lg font-medium text-muted-foreground">
              No scraping sessions found
            </p>
            <p className="mt-1 text-sm text-muted-foreground/70">
              {filter !== "all"
                ? `No ${filter} sessions yet. Try a different platform or start scraping.`
                : "Start a new scraping session to see results here."}
            </p>
            <Link href="/scrape">
              <Button variant="default" size="sm" className="mt-4">
                <Zap className="mr-1.5 size-3.5" />
                Start Scraping
              </Button>
            </Link>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-3">
          {paginated.map((session) => (
            <Link key={session.id} href={`/history/${session.id}`}>
              <Card className="group cursor-pointer border-border/50 transition-all duration-200 hover:border-primary/30 hover:bg-card/80">
                <CardContent className="flex items-center gap-4 py-4">
                  <div className="flex-1 min-w-0 space-y-2.5">
                    {/* Badges row */}
                    <div className="flex items-center gap-2">
                      <span
                        className={`inline-flex items-center rounded-md border px-2 py-0.5 text-xs font-semibold uppercase tracking-wider ${PLATFORM_COLORS[session.platform] || "bg-secondary text-secondary-foreground"}`}
                      >
                        {session.platform}
                      </span>
                      <span
                        className={`inline-flex items-center rounded-md border px-2 py-0.5 text-xs font-medium capitalize ${STATUS_COLORS[session.status] || "bg-secondary text-secondary-foreground"}`}
                      >
                        {session.status}
                      </span>
                    </div>

                    {/* Job titles */}
                    <p className="text-sm font-medium text-foreground truncate">
                      {truncateJobTitles(session.job_titles)}
                    </p>

                    {/* Meta row */}
                    <div className="flex flex-wrap items-center gap-x-5 gap-y-1 text-xs text-muted-foreground">
                      <span className="flex items-center gap-1.5">
                        <MapPin className="size-3 text-muted-foreground/70" />
                        {session.location}
                      </span>
                      <span className="flex items-center gap-1.5">
                        <Briefcase className="size-3 text-muted-foreground/70" />
                        <span className="text-foreground/80 font-medium">
                          {session.total_jobs}
                        </span>{" "}
                        jobs
                        <span className="text-emerald-400/80 font-medium">
                          ({session.eligible_jobs} eligible)
                        </span>
                      </span>
                      <span className="flex items-center gap-1.5">
                        <Calendar className="size-3 text-muted-foreground/70" />
                        {formatDate(session.created_at)}
                      </span>
                    </div>
                  </div>

                  <ChevronRight className="size-5 text-muted-foreground/40 transition-transform duration-200 group-hover:translate-x-0.5 group-hover:text-primary" />
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-center gap-3 pt-2">
          <Button
            variant="outline"
            size="sm"
            disabled={page === 1}
            onClick={() => setPage(page - 1)}
          >
            Previous
          </Button>
          <span className="text-sm text-muted-foreground tabular-nums">
            Page{" "}
            <span className="text-foreground font-medium">{page}</span> of{" "}
            <span className="text-foreground font-medium">{totalPages}</span>
          </span>
          <Button
            variant="outline"
            size="sm"
            disabled={page === totalPages}
            onClick={() => setPage(page + 1)}
          >
            Next
          </Button>
        </div>
      )}
    </div>
  );
}
