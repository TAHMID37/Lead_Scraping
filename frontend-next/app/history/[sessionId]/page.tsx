"use client";

import { useEffect, useState, useRef } from "react";
import { useParams } from "next/navigation";
import { useApi } from "@/hooks/use-api";
import Link from "next/link";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { JobTable } from "@/components/jobs/job-table";
import {
  ArrowLeft,
  MapPin,
  Calendar,
  Clock,
  Briefcase,
  CheckCircle2,
  XCircle,
  Timer,
  AlertTriangle,
} from "lucide-react";
import type { ScrapeSession } from "@/lib/types";

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

function computeDuration(start: string, end?: string): string {
  if (!end) return "--";
  const ms = new Date(end).getTime() - new Date(start).getTime();
  if (ms < 1000) return "<1s";
  const seconds = Math.floor(ms / 1000);
  if (seconds < 60) return `${seconds}s`;
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = seconds % 60;
  return `${minutes}m ${remainingSeconds}s`;
}

export default function SessionDetailPage() {
  const params = useParams();
  const sessionId = params.sessionId as string;
  const api = useApi();
  const apiRef = useRef(api);
  apiRef.current = api;

  const [session, setSession] = useState<ScrapeSession | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchSession() {
      try {
        const res = await apiRef.current.get(`/api/sessions/${sessionId}`);
        setSession(res.data);
      } catch {
        setSession(null);
      } finally {
        setLoading(false);
      }
    }
    fetchSession();
  }, [sessionId]);

  function formatDate(dateStr: string) {
    return new Date(dateStr).toLocaleDateString("en-AU", {
      day: "numeric",
      month: "short",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  }

  if (loading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-10 w-48" />
        <Skeleton className="h-48 w-full rounded-lg" />
        <Skeleton className="h-64 w-full rounded-lg" />
      </div>
    );
  }

  if (!session) {
    return (
      <div className="space-y-4">
        <Link href="/history">
          <Button variant="ghost" size="sm">
            <ArrowLeft className="mr-1.5 size-4" />
            Back to History
          </Button>
        </Link>
        <Card className="border-dashed">
          <CardContent className="flex flex-col items-center justify-center py-16 text-center">
            <div className="mb-4 rounded-full bg-muted p-4">
              <AlertTriangle className="size-8 text-muted-foreground" />
            </div>
            <p className="text-lg font-medium text-muted-foreground">
              Session not found
            </p>
            <p className="mt-1 text-sm text-muted-foreground/70">
              This session may have been deleted or the ID is invalid.
            </p>
          </CardContent>
        </Card>
      </div>
    );
  }

  const notEligible = session.total_jobs - session.eligible_jobs;

  return (
    <div className="space-y-6">
      {/* Back + Header */}
      <div className="flex items-center gap-3">
        <Link href="/history">
          <Button
            variant="outline"
            size="sm"
            className="gap-1.5 border-border/50"
          >
            <ArrowLeft className="size-3.5" />
            Back
          </Button>
        </Link>
        <div className="min-w-0">
          <h1 className="font-[family-name:var(--font-heading)] text-2xl font-bold tracking-tight">
            Session Detail
          </h1>
          <p className="truncate text-xs text-muted-foreground font-mono">
            {sessionId}
          </p>
        </div>
      </div>

      {/* Session Summary Card */}
      <Card className="border-border/50">
        <CardContent className="space-y-5 pt-6">
          {/* Badges */}
          <div className="flex flex-wrap items-center gap-2">
            <span
              className={`inline-flex items-center rounded-md border px-2.5 py-0.5 text-xs font-semibold uppercase tracking-wider ${PLATFORM_COLORS[session.platform] || "bg-secondary text-secondary-foreground"}`}
            >
              {session.platform}
            </span>
            <span
              className={`inline-flex items-center rounded-md border px-2.5 py-0.5 text-xs font-medium capitalize ${STATUS_COLORS[session.status] || "bg-secondary text-secondary-foreground"}`}
            >
              {session.status}
            </span>
          </div>

          {/* Job titles as badges */}
          <div>
            <p className="mb-2 text-xs font-medium uppercase tracking-wider text-muted-foreground">
              Job Titles Searched
            </p>
            <div className="flex flex-wrap gap-1.5">
              {session.job_titles.map((title, i) => (
                <Badge
                  key={i}
                  variant="outline"
                  className="border-border/60 text-foreground/80"
                >
                  {title}
                </Badge>
              ))}
            </div>
          </div>

          {/* Location + dates */}
          <div className="flex flex-wrap gap-x-6 gap-y-2 text-sm text-muted-foreground">
            <span className="flex items-center gap-1.5">
              <MapPin className="size-3.5 text-primary/70" />
              {session.location}
            </span>
            <span className="flex items-center gap-1.5">
              <Calendar className="size-3.5 text-primary/70" />
              {formatDate(session.created_at)}
            </span>
            {session.completed_at && (
              <span className="flex items-center gap-1.5">
                <Clock className="size-3.5 text-primary/70" />
                Completed {formatDate(session.completed_at)}
              </span>
            )}
          </div>

          {/* Stats Grid */}
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
            <div className="rounded-lg border border-border/50 bg-secondary/30 p-4 text-center">
              <Briefcase className="mx-auto mb-1.5 size-4 text-muted-foreground" />
              <p className="text-2xl font-bold tabular-nums">
                {session.total_jobs}
              </p>
              <p className="text-xs text-muted-foreground">Total Jobs</p>
            </div>
            <div className="rounded-lg border border-emerald-500/20 bg-emerald-500/5 p-4 text-center">
              <CheckCircle2 className="mx-auto mb-1.5 size-4 text-emerald-400" />
              <p className="text-2xl font-bold tabular-nums text-emerald-400">
                {session.eligible_jobs}
              </p>
              <p className="text-xs text-muted-foreground">Eligible</p>
            </div>
            <div className="rounded-lg border border-red-500/20 bg-red-500/5 p-4 text-center">
              <XCircle className="mx-auto mb-1.5 size-4 text-red-400" />
              <p className="text-2xl font-bold tabular-nums text-red-400">
                {notEligible}
              </p>
              <p className="text-xs text-muted-foreground">Not Eligible</p>
            </div>
            <div className="rounded-lg border border-border/50 bg-secondary/30 p-4 text-center">
              <Timer className="mx-auto mb-1.5 size-4 text-muted-foreground" />
              <p className="text-2xl font-bold tabular-nums">
                {computeDuration(session.started_at, session.completed_at)}
              </p>
              <p className="text-xs text-muted-foreground">Duration</p>
            </div>
          </div>

          {/* Error message */}
          {session.error_message && (
            <div className="rounded-lg border border-red-500/30 bg-red-500/5 p-3">
              <div className="flex items-start gap-2">
                <AlertTriangle className="mt-0.5 size-4 shrink-0 text-red-400" />
                <p className="text-sm text-red-400">{session.error_message}</p>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Jobs Table */}
      <Card className="border-border/50">
        <CardHeader>
          <CardTitle className="font-[family-name:var(--font-heading)] text-lg tracking-tight">
            Jobs ({session.jobs?.length ?? 0})
          </CardTitle>
        </CardHeader>
        <CardContent>
          <JobTable jobs={session.jobs ?? []} />
        </CardContent>
      </Card>
    </div>
  );
}
