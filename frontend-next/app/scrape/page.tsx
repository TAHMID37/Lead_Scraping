"use client";

import { useState } from "react";
import { useScrape } from "@/lib/scrape-context";
import { toast } from "sonner";
import type { Platform } from "@/lib/types";
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
import { JobTitleSelector } from "@/components/scrape/job-title-selector";
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

const PLATFORMS: { value: Platform; label: string; color: string }[] = [
  { value: "seek", label: "Seek", color: "text-purple-400 border-purple-400" },
  { value: "careerone", label: "CareerOne", color: "text-amber-400 border-amber-400" },
  { value: "indeed", label: "Indeed", color: "text-blue-400 border-blue-400" },
];

export default function ScrapePage() {
  const { activeScrapes, startScrape, clearScrape } = useScrape();
  const [platform, setPlatform] = useState<Platform>("seek");
  const [selectedTitles, setSelectedTitles] = useState<string[]>([]);
  const [location, setLocation] = useState<string>("");
  const [maxPages, setMaxPages] = useState(2);
  const [submitting, setSubmitting] = useState(false);

  // Find active/completed scrapes to display
  const currentScrapes = activeScrapes.filter((s) => s.platform === platform);
  const latestScrape = currentScrapes[currentScrapes.length - 1];

  const isRunning = latestScrape && !["completed", "failed"].includes(latestScrape.status);
  const canSubmit = selectedTitles.length > 0 && location !== "" && !submitting && !isRunning;

  async function handleScrape() {
    if (!canSubmit) return;

    setSubmitting(true);
    const sessionId = await startScrape(platform, selectedTitles, location, maxPages);
    setSubmitting(false);

    if (sessionId) {
      toast.success(`Scrape started for ${platform} — you can navigate away safely`);
    } else {
      toast.error("Failed to start scrape");
    }
  }

  const jobs = latestScrape?.jobs ?? [];
  const eligibleCount = jobs.filter((j) => j.anzsco_assessment?.eligible).length;
  const hasResults = latestScrape?.status === "completed" && jobs.length > 0;
  const hasFailed = latestScrape?.status === "failed";

  return (
    <div className="space-y-5">
      {/* Header */}
      <div>
        <h1 className="font-[family-name:var(--font-heading)] text-2xl font-bold tracking-tight">
          Scrape Jobs
        </h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Search and scrape job listings from Australian platforms
        </p>
      </div>

      {/* Unified scraper card */}
      <Card className="border-border/50 bg-card/80 overflow-hidden">
        {/* Platform tabs as card header */}
        <div className="flex border-b border-border/50">
          {PLATFORMS.map((p) => (
            <button
              key={p.value}
              onClick={() => setPlatform(p.value)}
              className={`
                relative px-5 py-3 text-sm font-medium transition-colors
                font-[family-name:var(--font-heading)] tracking-wide
                ${platform === p.value
                  ? `${p.color} bg-card`
                  : "text-muted-foreground hover:text-foreground hover:bg-accent/50"
                }
              `}
            >
              {p.label}
              {platform === p.value && (
                <span className={`absolute bottom-0 left-0 right-0 h-0.5 ${p.color.split(" ")[1] ? `bg-current` : "bg-primary"}`} />
              )}
            </button>
          ))}
        </div>

        {/* Form */}
        <CardContent className="p-5 space-y-4">
          {/* Job Titles */}
          <div className="space-y-1.5">
            <Label className="text-[10px] uppercase tracking-wider text-muted-foreground">
              Job Titles
            </Label>
            <JobTitleSelector
              selected={selectedTitles}
              onChange={setSelectedTitles}
            />
          </div>

          {/* Location + Pages + Button */}
          <div className="flex flex-col sm:flex-row gap-3 sm:items-end">
            <div className="flex-1 space-y-1.5">
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

            <div className="w-20 space-y-1.5">
              <Label className="text-[10px] uppercase tracking-wider text-muted-foreground">
                Pages
              </Label>
              <Input
                type="number"
                min={1}
                max={5}
                value={maxPages}
                onChange={(e) =>
                  setMaxPages(Math.min(5, Math.max(1, parseInt(e.target.value) || 1)))
                }
                className="h-9 bg-background/50 border-border/50"
              />
            </div>

            <Button
              onClick={handleScrape}
              disabled={!canSubmit}
              size="sm"
              className="h-9 px-6 font-[family-name:var(--font-heading)] text-[11px] tracking-wider uppercase shrink-0"
            >
              {submitting || isRunning ? (
                <>
                  <Loader2 className="mr-1.5 size-3.5 animate-spin" />
                  {isRunning ? (
                    latestScrape.status === "scraping" ? "Scraping" :
                    latestScrape.status === "validating" ? "Validating" :
                    "Enriching"
                  ) : "Starting"}
                </>
              ) : (
                <>
                  <Play className="mr-1.5 size-3.5" />
                  Start Scrape
                </>
              )}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Status */}
      {latestScrape && (
        <div className="flex items-center gap-2.5 rounded-lg border border-border/50 bg-card/60 px-4 py-2.5">
          {isRunning ? (
            <>
              <Loader2 className="size-3.5 animate-spin text-primary" />
              <span className="text-sm text-muted-foreground">
                {latestScrape.status === "scraping" && `Scraping ${platform} for ${latestScrape.jobTitles.length} title(s) in ${latestScrape.location}...`}
                {latestScrape.status === "validating" && "Validating jobs against ANZSCO 482..."}
                {latestScrape.status === "enriching" && "Enriching company information..."}
              </span>
              <span className="ml-auto text-[10px] uppercase tracking-wider text-muted-foreground">
                Navigate freely — scrape continues in background
              </span>
            </>
          ) : hasFailed ? (
            <>
              <XCircle className="size-3.5 text-destructive" />
              <span className="text-sm text-destructive">Error: {latestScrape.error || "Scrape failed"}</span>
              <button
                onClick={() => clearScrape(latestScrape.sessionId)}
                className="ml-auto text-xs text-muted-foreground hover:text-foreground"
              >
                Dismiss
              </button>
            </>
          ) : (
            <>
              <CheckCircle className="size-3.5 text-emerald-400" />
              <span className="text-sm text-emerald-400">
                Scrape completed — {latestScrape.totalJobs} jobs found
              </span>
              <button
                onClick={() => clearScrape(latestScrape.sessionId)}
                className="ml-auto text-xs text-muted-foreground hover:text-foreground"
              >
                Dismiss
              </button>
            </>
          )}
        </div>
      )}

      {/* Loading Skeleton */}
      {isRunning && (
        <div className="space-y-2">
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} className="h-10 w-full rounded-md" />
          ))}
        </div>
      )}

      {/* Results */}
      {hasResults && (
        <div className="space-y-4">
          {/* Stats row */}
          <div className="grid gap-3 grid-cols-3">
            <div className="flex items-center gap-3 rounded-lg border border-border/50 bg-card/80 px-4 py-2.5">
              <Briefcase className="size-4 text-primary" />
              <span className="font-[family-name:var(--font-heading)] text-lg font-bold tabular-nums">{jobs.length}</span>
              <span className="text-[10px] uppercase tracking-wider text-muted-foreground">Jobs</span>
            </div>
            <div className="flex items-center gap-3 rounded-lg border border-emerald-500/20 bg-emerald-500/5 px-4 py-2.5">
              <ShieldCheck className="size-4 text-emerald-400" />
              <span className="font-[family-name:var(--font-heading)] text-lg font-bold tabular-nums text-emerald-400">{eligibleCount}</span>
              <span className="text-[10px] uppercase tracking-wider text-muted-foreground">Eligible</span>
            </div>
            <div className="flex items-center gap-3 rounded-lg border border-red-500/20 bg-red-500/5 px-4 py-2.5">
              <ShieldX className="size-4 text-red-400" />
              <span className="font-[family-name:var(--font-heading)] text-lg font-bold tabular-nums text-red-400">{jobs.length - eligibleCount}</span>
              <span className="text-[10px] uppercase tracking-wider text-muted-foreground">Ineligible</span>
            </div>
          </div>

          {/* Job Table */}
          <Card className="border-border/50 bg-card/80">
            <CardContent className="pt-4">
              <JobTable jobs={jobs} />
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
