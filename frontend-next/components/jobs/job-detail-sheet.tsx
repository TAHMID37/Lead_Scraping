"use client";

import { useMemo } from "react";
import type { Job } from "@/lib/types";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetDescription,
} from "@/components/ui/sheet";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  ExternalLink,
  MapPin,
  Building2,
  Calendar,
  ShieldCheck,
  ShieldX,
  Hash,
  Briefcase,
  DollarSign,
} from "lucide-react";

interface JobDetailSheetProps {
  job: Job | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

function getConfidenceColor(score: number): string {
  if (score >= 0.8) return "text-emerald-400";
  if (score >= 0.6) return "text-amber-400";
  return "text-red-400";
}

function getConfidenceBarColor(score: number): string {
  if (score >= 0.8) return "bg-emerald-400";
  if (score >= 0.6) return "bg-amber-400";
  return "bg-red-400";
}

/**
 * Cleans up scraped markdown:
 * - Decodes HTML entities (&amp;nbsp; -> space, &amp; -> &)
 * - Strips Indeed/Seek nav chrome (e.g. "WhatWhereFind Jobs", star ratings)
 * - Removes excessive blank lines
 */
function cleanDescription(raw: string): string {
  let text = raw;
  // Decode HTML entities
  text = text.replace(/&amp;nbsp;/g, " ");
  text = text.replace(/&amp;/g, "&");
  text = text.replace(/&lt;/g, "<");
  text = text.replace(/&gt;/g, ">");
  text = text.replace(/&quot;/g, '"');
  text = text.replace(/&#39;/g, "'");

  // Try to find "Full job description" or "Job description" header and start from there
  const fullDescMatch = text.match(/## Full job description\n([\s\S]*)/i);
  if (fullDescMatch) {
    text = fullDescMatch[1];
  } else {
    // Otherwise try to strip common nav chrome lines at the top
    const lines = text.split("\n");
    let startIdx = 0;
    for (let i = 0; i < Math.min(lines.length, 20); i++) {
      const line = lines[i].trim();
      // Skip empty lines, nav text, star ratings, page headers
      if (
        !line ||
        /^WhatWhere/i.test(line) ||
        /^Find Jobs/i.test(line) ||
        /^\d+\.\d+ out of \d+ stars?$/i.test(line) ||
        /^\d+\.\d+\d+\.\d+/i.test(line) ||
        /^(Full-time|Part-time|Casual|Contract|Temporary)$/i.test(line) ||
        /^## (Job details|Location|Job type)$/i.test(line) ||
        /^\*$/i.test(line)
      ) {
        startIdx = i + 1;
        continue;
      }
      // Stop if we hit real content (a heading with substance or a paragraph)
      if (line.startsWith("**") || (line.length > 50 && !line.startsWith("#"))) {
        break;
      }
    }
    if (startIdx > 0 && startIdx < lines.length) {
      text = lines.slice(startIdx).join("\n");
    }
  }

  // Collapse 3+ blank lines into 2
  text = text.replace(/\n{3,}/g, "\n\n");
  return text.trim();
}

export function JobDetailSheet({ job, open, onOpenChange }: JobDetailSheetProps) {
  if (!job) return null;

  const assessment = job.anzsco_assessment;
  const confidencePercent = assessment
    ? Math.round(assessment.confidence_score * 100)
    : 0;

  const cleanedDescription = useMemo(
    () => cleanDescription(job.job_description || ""),
    [job.job_description]
  );

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent side="right" className="w-full sm:!max-w-3xl border-border/50 bg-card p-0">
        <SheetHeader className="px-6 pt-6 pb-4 border-b border-border/50">
          <SheetTitle className="font-[family-name:var(--font-heading)] text-xl tracking-tight leading-snug pr-8">
            {job.job_title}
          </SheetTitle>
          <SheetDescription className="sr-only">
            Job details for {job.job_title}
          </SheetDescription>

          {/* Meta Info */}
          <div className="flex flex-wrap gap-x-5 gap-y-2 pt-2">
            {job.employer_name && (
              <span className="flex items-center gap-1.5 text-sm text-muted-foreground">
                <Building2 className="size-3.5 text-primary/70" />
                {job.employer_name}
              </span>
            )}
            {job.location && (
              <span className="flex items-center gap-1.5 text-sm text-muted-foreground">
                <MapPin className="size-3.5 text-primary/70" />
                {job.location}
              </span>
            )}
            {job.posted_date && job.posted_date !== "Unknown" && (
              <span className="flex items-center gap-1.5 text-sm text-muted-foreground">
                <Calendar className="size-3.5 text-primary/70" />
                {job.posted_date}
              </span>
            )}
            {job.salary && (
              <span className="flex items-center gap-1.5 text-sm font-medium text-foreground">
                <DollarSign className="size-3.5 text-primary/70" />
                {job.salary}
              </span>
            )}
          </div>
        </SheetHeader>

        <ScrollArea className="h-[calc(100vh-10rem)]">
          <div className="space-y-6 px-6 py-5">
            {/* ANZSCO Assessment */}
            <div className="space-y-3">
              <h3 className="font-[family-name:var(--font-heading)] text-xs uppercase tracking-wider text-muted-foreground">
                ANZSCO Assessment
              </h3>
              {assessment ? (
                <div className="space-y-4 rounded-lg border border-border/50 bg-background/30 p-4">
                  {/* Eligibility Row */}
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-muted-foreground">Eligibility</span>
                    {assessment.eligible ? (
                      <div className="flex items-center gap-1.5">
                        <ShieldCheck className="size-4 text-emerald-400" />
                        <Badge className="bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 hover:bg-emerald-500/15">
                          Eligible
                        </Badge>
                      </div>
                    ) : (
                      <div className="flex items-center gap-1.5">
                        <ShieldX className="size-4 text-red-400" />
                        <Badge className="bg-red-500/10 text-red-400 border border-red-500/20 hover:bg-red-500/15">
                          Not Eligible
                        </Badge>
                      </div>
                    )}
                  </div>

                  {/* Occupation */}
                  {assessment.occupation && (
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-muted-foreground flex items-center gap-1.5">
                        <Briefcase className="size-3.5" />
                        Occupation
                      </span>
                      <span className="font-[family-name:var(--font-heading)] text-xs tracking-tight text-right max-w-[60%]">
                        {assessment.occupation}
                      </span>
                    </div>
                  )}

                  {/* ANZSCO Code */}
                  {assessment.anzsco_code && (
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-muted-foreground flex items-center gap-1.5">
                        <Hash className="size-3.5" />
                        ANZSCO Code
                      </span>
                      <Badge
                        variant="outline"
                        className="font-[family-name:var(--font-heading)] text-xs tracking-wider border-primary/30 text-primary"
                      >
                        {assessment.anzsco_code}
                      </Badge>
                    </div>
                  )}

                  {/* Confidence */}
                  <div className="space-y-2">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-muted-foreground">Confidence</span>
                      <span
                        className={`font-[family-name:var(--font-heading)] text-sm font-semibold tracking-tight ${getConfidenceColor(
                          assessment.confidence_score
                        )}`}
                      >
                        {confidencePercent}%
                      </span>
                    </div>
                    <div className="h-1.5 w-full rounded-full bg-background/80 overflow-hidden">
                      <div
                        className={`h-full rounded-full transition-all ${getConfidenceBarColor(
                          assessment.confidence_score
                        )}`}
                        style={{ width: `${confidencePercent}%` }}
                      />
                    </div>
                  </div>

                  {/* Reason */}
                  {assessment.reason && (
                    <div className="rounded-md bg-background/50 p-3 text-sm">
                      <span className="text-xs uppercase tracking-wider text-muted-foreground block mb-1">
                        Reason
                      </span>
                      <span className="text-foreground/80 leading-relaxed">
                        {assessment.reason}
                      </span>
                    </div>
                  )}
                </div>
              ) : (
                <div className="rounded-lg border border-border/30 bg-background/20 p-4 text-center">
                  <p className="text-sm text-muted-foreground">
                    Assessment not yet available.
                  </p>
                </div>
              )}
            </div>

            <Separator className="bg-border/50" />

            {/* Job Description */}
            <div className="space-y-3">
              <h3 className="font-[family-name:var(--font-heading)] text-xs uppercase tracking-wider text-muted-foreground">
                Job Description
              </h3>
              <div className="markdown-content prose-sm text-sm leading-relaxed text-muted-foreground">
                {cleanedDescription ? (
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>
                    {cleanedDescription}
                  </ReactMarkdown>
                ) : (
                  <p className="italic text-muted-foreground/60">No description available</p>
                )}
              </div>
            </div>

            {/* Link to Original */}
            {job.url && (
              <>
                <Separator className="bg-border/50" />
                <a
                  href={job.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-2 rounded-lg border border-primary/20 bg-primary/5 px-4 py-2.5 text-sm font-medium text-primary hover:bg-primary/10 transition-colors"
                >
                  View Original Posting
                  <ExternalLink className="size-3.5" />
                </a>
              </>
            )}
          </div>
        </ScrollArea>
      </SheetContent>
    </Sheet>
  );
}
