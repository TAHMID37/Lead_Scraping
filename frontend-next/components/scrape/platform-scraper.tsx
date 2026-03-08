"use client";

import { useState } from "react";
import { useApi } from "@/hooks/use-api";
import { toast } from "sonner";
import type { Platform, Job } from "@/lib/types";
import { LOCATIONS } from "@/lib/constants";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import { JobTitleSelector } from "./job-title-selector";
import { JobTable } from "@/components/jobs/job-table";
import {
  Loader2,
  Play,
  CheckCircle,
  XCircle,
  Briefcase,
  ShieldCheck,
  ShieldX,
  MapPin,
} from "lucide-react";

interface PlatformScraperProps {
  platform: Platform;
}

function formatLocation(location: string, platform: Platform): string {
  switch (platform) {
    case "seek":
      return location.replace(/\s+/g, "-");
    case "careerone":
      return location.split(" ")[0];
    default:
      return location;
  }
}

export function PlatformScraper({ platform }: PlatformScraperProps) {
  const api = useApi();

  const [selectedTitles, setSelectedTitles] = useState<string[]>([]);
  const [location, setLocation] = useState<string>("");
  const [maxPages, setMaxPages] = useState(2);
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState<string>("");
  const [jobs, setJobs] = useState<Job[]>([]);
  const [hasResults, setHasResults] = useState(false);

  const canSubmit = selectedTitles.length > 0 && location !== "" && !loading;

  async function handleScrape() {
    if (!canSubmit) return;

    setLoading(true);
    setStatus("Initializing scraper...");
    setJobs([]);
    setHasResults(false);

    try {
      const formattedLocation = formatLocation(location, platform);

      setStatus(`Scraping ${platform} for ${selectedTitles.length} title(s) in ${location}...`);

      const response = await api.post(`/api/scrape/${platform}`, {
        job_titles: selectedTitles,
        location: formattedLocation,
        max_pages: maxPages,
      });

      const data = response.data;
      const sessionId = data.session_id;

      if (sessionId) {
        setStatus("Fetching session results...");
        const sessionResponse = await api.get(`/api/sessions/${sessionId}`);
        const sessionData = sessionResponse.data;
        if (sessionData.jobs) {
          setJobs(sessionData.jobs);
        }
      } else if (data.jobs) {
        setJobs(data.jobs);
      } else if (Array.isArray(data)) {
        setJobs(data);
      }

      setHasResults(true);
      setStatus("Scrape completed");
      toast.success(
        `Successfully scraped ${data.jobs?.length ?? data.length ?? 0} jobs from ${platform}`
      );
    } catch (error: unknown) {
      const message =
        error instanceof Error ? error.message : "An error occurred";
      setStatus(`Error: ${message}`);
      toast.error(`Scrape failed: ${message}`);
    } finally {
      setLoading(false);
    }
  }

  const eligibleCount = jobs.filter((j) => j.anzsco_assessment?.eligible).length;

  return (
    <div className="space-y-6">
      {/* Scraper Form - Compact */}
      <Card className="border-border/50 bg-card/80 backdrop-blur-sm">
        <CardContent className="pt-5 pb-4 space-y-4">
          {/* Row 1: Job Titles */}
          <div className="space-y-1.5">
            <Label className="text-[10px] uppercase tracking-wider text-muted-foreground">
              Job Titles
            </Label>
            <JobTitleSelector
              selected={selectedTitles}
              onChange={setSelectedTitles}
            />
          </div>

          {/* Row 2: Location + Max Pages + Submit - all inline */}
          <div className="grid gap-3 sm:grid-cols-[1fr_100px_auto]">
            <div className="space-y-1.5">
              <Label className="text-[10px] uppercase tracking-wider text-muted-foreground">
                Location
              </Label>
              <Select value={location} onValueChange={(v) => setLocation(v ?? "")}>
                <SelectTrigger className="h-9 bg-background/50 border-border/50">
                  <div className="flex items-center gap-2">
                    <MapPin className="size-3 text-muted-foreground" />
                    <SelectValue placeholder="Select location" />
                  </div>
                </SelectTrigger>
                <SelectContent>
                  {LOCATIONS.map((loc) => (
                    <SelectItem key={loc} value={loc}>
                      {loc}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-1.5">
              <Label className="text-[10px] uppercase tracking-wider text-muted-foreground">
                Pages
              </Label>
              <Input
                type="number"
                min={1}
                max={5}
                value={maxPages}
                onChange={(e) =>
                  setMaxPages(
                    Math.min(5, Math.max(1, parseInt(e.target.value) || 1))
                  )
                }
                className="h-9 bg-background/50 border-border/50"
              />
            </div>

            <div className="flex items-end">
              <Button
                onClick={handleScrape}
                disabled={!canSubmit}
                size="sm"
                className="h-9 px-5 bg-primary hover:bg-primary/90 text-primary-foreground font-[family-name:var(--font-heading)] text-[11px] tracking-wider uppercase"
              >
                {loading ? (
                  <>
                    <Loader2 className="mr-1.5 size-3.5 animate-spin" />
                    Scraping
                  </>
                ) : (
                  <>
                    <Play className="mr-1.5 size-3.5" />
                    Scrape
                  </>
                )}
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Status Bar */}
      {status && (
        <div className="flex items-center gap-3 rounded-lg border border-border/50 bg-card/60 px-4 py-3 backdrop-blur-sm">
          {loading ? (
            <div className="flex items-center gap-2">
              <div className="relative">
                <Loader2 className="size-4 animate-spin text-primary" />
                <div className="absolute inset-0 size-4 animate-ping rounded-full bg-primary/20" />
              </div>
              <span className="text-sm text-muted-foreground">{status}</span>
            </div>
          ) : status.startsWith("Error") ? (
            <>
              <XCircle className="size-4 text-destructive" />
              <span className="text-sm text-destructive">{status}</span>
            </>
          ) : (
            <>
              <CheckCircle className="size-4 text-primary" />
              <span className="text-sm text-primary">{status}</span>
            </>
          )}
        </div>
      )}

      {/* Loading Skeleton */}
      {loading && !hasResults && (
        <Card className="border-border/50 bg-card/60">
          <CardContent className="space-y-3 py-6">
            <div className="flex items-center gap-3 mb-4">
              <Skeleton className="h-4 w-4 rounded-full" />
              <Skeleton className="h-4 w-48" />
            </div>
            <Skeleton className="h-10 w-full" />
            <Skeleton className="h-10 w-full" />
            <Skeleton className="h-10 w-full" />
            <Skeleton className="h-10 w-3/4" />
          </CardContent>
        </Card>
      )}

      {/* Results */}
      {hasResults && (
        <>
          {/* Stat Cards - Compact row */}
          <div className="grid gap-3 sm:grid-cols-3">
            <div className="flex items-center gap-3 rounded-lg border border-border/50 bg-card/80 px-4 py-3">
              <Briefcase className="size-4 text-primary" />
              <div className="flex items-baseline gap-2">
                <span className="font-[family-name:var(--font-heading)] text-xl font-bold tabular-nums">{jobs.length}</span>
                <span className="text-[10px] uppercase tracking-wider text-muted-foreground">Jobs</span>
              </div>
            </div>
            <div className="flex items-center gap-3 rounded-lg border border-emerald-500/20 bg-emerald-500/5 px-4 py-3">
              <ShieldCheck className="size-4 text-emerald-400" />
              <div className="flex items-baseline gap-2">
                <span className="font-[family-name:var(--font-heading)] text-xl font-bold tabular-nums text-emerald-400">{eligibleCount}</span>
                <span className="text-[10px] uppercase tracking-wider text-muted-foreground">Eligible</span>
              </div>
            </div>
            <div className="flex items-center gap-3 rounded-lg border border-red-500/20 bg-red-500/5 px-4 py-3">
              <ShieldX className="size-4 text-red-400" />
              <div className="flex items-baseline gap-2">
                <span className="font-[family-name:var(--font-heading)] text-xl font-bold tabular-nums text-red-400">{jobs.length - eligibleCount}</span>
                <span className="text-[10px] uppercase tracking-wider text-muted-foreground">Ineligible</span>
              </div>
            </div>
          </div>

          {/* Job Table */}
          <Card className="border-border/50 bg-card/80 backdrop-blur-sm">
            <CardContent className="pt-4">
              <JobTable jobs={jobs} />
            </CardContent>
          </Card>
        </>
      )}
    </div>
  );
}
