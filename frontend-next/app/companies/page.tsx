"use client";

import { useEffect, useState, useRef } from "react";
import { useApi } from "@/hooks/use-api";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
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
  Building2,
  Info,
  CheckCircle2,
  XCircle,
  CloudOff,
} from "lucide-react";
import type { Company } from "@/lib/types";

const SOURCE_COLORS: Record<string, string> = {
  indeed: "bg-blue-500/15 text-blue-400 border-blue-500/25",
  seek: "bg-purple-500/15 text-purple-400 border-purple-500/25",
  careerone: "bg-amber-500/15 text-amber-400 border-amber-500/25",
};

function hubspotStatusBadge(status: string | null | undefined) {
  if (!status || status === "not_synced") {
    return (
      <span className="inline-flex items-center gap-1 text-xs text-muted-foreground/60">
        <CloudOff className="size-3" />
        Not Synced
      </span>
    );
  }
  switch (status) {
    case "created":
      return (
        <span className="inline-flex items-center rounded-md border border-emerald-500/25 bg-emerald-500/15 px-2 py-0.5 text-xs font-medium text-emerald-400">
          Synced
        </span>
      );
    case "updated":
      return (
        <span className="inline-flex items-center rounded-md border border-blue-500/25 bg-blue-500/15 px-2 py-0.5 text-xs font-medium text-blue-400">
          Updated
        </span>
      );
    case "failed":
      return (
        <span className="inline-flex items-center rounded-md border border-red-500/25 bg-red-500/15 px-2 py-0.5 text-xs font-medium text-red-400">
          Failed
        </span>
      );
    default:
      return (
        <span className="inline-flex items-center gap-1 text-xs text-muted-foreground/60">
          <CloudOff className="size-3" />
          Not Synced
        </span>
      );
  }
}

export default function CompaniesPage() {
  const api = useApi();
  const apiRef = useRef(api);
  apiRef.current = api;
  const [companies, setCompanies] = useState<Company[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchCompanies() {
      try {
        const res = await apiRef.current.get("/api/companies");
        const data = res.data;
        setCompanies(data.companies || []);
      } catch {
        setCompanies([]);
      } finally {
        setLoading(false);
      }
    }
    fetchCompanies();
  }, []);

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="font-[family-name:var(--font-heading)] text-3xl font-bold tracking-tight">
          Companies
        </h1>
        <p className="mt-1 text-muted-foreground">
          Companies discovered from scraped job listings
        </p>
      </div>

      {/* HubSpot info note */}
      {!loading && companies.length > 0 && (
        <div className="flex items-start gap-2.5 rounded-lg border border-primary/20 bg-primary/5 px-4 py-3">
          <Info className="mt-0.5 size-4 shrink-0 text-primary" />
          <p className="text-sm text-primary/80">
            HubSpot sync requires a valid API key configured in{" "}
            <a href="/settings" className="font-medium underline underline-offset-2 hover:text-primary">
              Settings
            </a>
            .
          </p>
        </div>
      )}

      {/* Companies Table */}
      <Card className="border-border/50">
        <CardHeader>
          <CardTitle className="font-[family-name:var(--font-heading)] text-lg tracking-tight">
            All Companies
          </CardTitle>
          {!loading && companies.length > 0 && (
            <CardDescription>
              {companies.length} {companies.length === 1 ? "company" : "companies"} found
            </CardDescription>
          )}
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="space-y-3">
              {Array.from({ length: 5 }).map((_, i) => (
                <Skeleton key={i} className="h-12 w-full rounded-md" />
              ))}
            </div>
          ) : companies.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-16 text-center">
              <div className="mb-4 rounded-full bg-muted p-4">
                <Building2 className="size-8 text-muted-foreground" />
              </div>
              <p className="text-lg font-medium text-muted-foreground">
                No companies found
              </p>
              <p className="mt-1 text-sm text-muted-foreground/70">
                Start scraping to discover companies from job listings.
              </p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow className="border-border/50 hover:bg-transparent">
                    <TableHead className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                      Name
                    </TableHead>
                    <TableHead className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                      Industry
                    </TableHead>
                    <TableHead className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                      Source
                    </TableHead>
                    <TableHead className="text-center text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                      Jobs
                    </TableHead>
                    <TableHead className="text-center text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                      ANZSCO
                    </TableHead>
                    <TableHead className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                      HubSpot
                    </TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {companies.map((company) => (
                    <TableRow
                      key={company.id}
                      className="border-border/30 transition-colors hover:bg-secondary/30"
                    >
                      <TableCell className="font-medium text-foreground">
                        {company.name}
                      </TableCell>
                      <TableCell className="text-muted-foreground">
                        {company.industry || (
                          <span className="text-muted-foreground/40">--</span>
                        )}
                      </TableCell>
                      <TableCell>
                        <span
                          className={`inline-flex items-center rounded-md border px-2 py-0.5 text-xs font-semibold uppercase tracking-wider ${SOURCE_COLORS[company.source] || "bg-secondary text-secondary-foreground"}`}
                        >
                          {company.source}
                        </span>
                      </TableCell>
                      <TableCell className="text-center tabular-nums font-medium">
                        {company.job_count}
                      </TableCell>
                      <TableCell className="text-center">
                        {company.anzsco_eligible ? (
                          <CheckCircle2 className="mx-auto size-4 text-emerald-400" />
                        ) : (
                          <XCircle className="mx-auto size-4 text-muted-foreground/40" />
                        )}
                      </TableCell>
                      <TableCell>
                        {hubspotStatusBadge(company.hubspot_status)}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
