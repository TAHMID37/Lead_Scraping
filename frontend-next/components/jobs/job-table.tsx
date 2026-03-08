"use client";

import { useState, useMemo } from "react";
import {
  useReactTable,
  getCoreRowModel,
  getSortedRowModel,
  type SortingState,
  type ColumnDef,
  flexRender,
} from "@tanstack/react-table";
import type { Job } from "@/lib/types";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { JobDetailSheet } from "./job-detail-sheet";
import { ArrowUpDown, Eye, CheckCircle, XCircle, Minus } from "lucide-react";

interface JobTableProps {
  jobs: Job[];
}

const platformBadgeColors: Record<string, string> = {
  indeed: "bg-blue-500/10 text-blue-400 border-blue-500/20",
  seek: "bg-purple-500/10 text-purple-400 border-purple-500/20",
  careerone: "bg-amber-500/10 text-amber-400 border-amber-500/20",
};

function getConfidenceColor(score: number): string {
  if (score >= 0.8) return "text-emerald-400";
  if (score >= 0.6) return "text-amber-400";
  return "text-red-400";
}

export function JobTable({ jobs }: JobTableProps) {
  const [sorting, setSorting] = useState<SortingState>([]);
  const [selectedJob, setSelectedJob] = useState<Job | null>(null);

  const columns: ColumnDef<Job>[] = useMemo(
    () => [
      {
        accessorKey: "job_title",
        header: ({ column }) => (
          <Button
            variant="ghost"
            size="sm"
            onClick={() =>
              column.toggleSorting(column.getIsSorted() === "asc")
            }
            className="text-[10px] uppercase tracking-wider text-muted-foreground hover:text-foreground -ml-3"
          >
            Job Title
            <ArrowUpDown className="ml-1 size-3" />
          </Button>
        ),
        cell: ({ row }) => (
          <span className="font-[family-name:var(--font-heading)] text-sm font-medium tracking-tight">
            {row.getValue("job_title")}
          </span>
        ),
      },
      {
        accessorKey: "employer_name",
        header: ({ column }) => (
          <Button
            variant="ghost"
            size="sm"
            onClick={() =>
              column.toggleSorting(column.getIsSorted() === "asc")
            }
            className="text-[10px] uppercase tracking-wider text-muted-foreground hover:text-foreground -ml-3"
          >
            Employer
            <ArrowUpDown className="ml-1 size-3" />
          </Button>
        ),
        cell: ({ row }) => (
          <span className="text-sm text-muted-foreground">
            {row.getValue("employer_name")}
          </span>
        ),
      },
      {
        accessorKey: "location",
        header: () => (
          <span className="text-[10px] uppercase tracking-wider text-muted-foreground">
            Location
          </span>
        ),
        cell: ({ row }) => (
          <span className="text-sm text-muted-foreground">
            {row.getValue("location")}
          </span>
        ),
      },
      {
        id: "platform",
        header: () => (
          <span className="text-[10px] uppercase tracking-wider text-muted-foreground">
            Platform
          </span>
        ),
        accessorKey: "platform",
        cell: ({ row }) => {
          const platform = row.original.platform;
          return (
            <Badge
              variant="outline"
              className={`font-[family-name:var(--font-heading)] text-[10px] tracking-wider capitalize ${
                platformBadgeColors[platform] || ""
              }`}
            >
              {platform}
            </Badge>
          );
        },
      },
      {
        id: "eligible",
        header: () => (
          <span className="text-[10px] uppercase tracking-wider text-muted-foreground">
            Eligible
          </span>
        ),
        accessorFn: (row) => row.anzsco_assessment?.eligible,
        cell: ({ row }) => {
          const assessment = row.original.anzsco_assessment;
          if (!assessment) {
            return <Minus className="size-4 text-muted-foreground/50" />;
          }
          return assessment.eligible ? (
            <CheckCircle className="size-4 text-emerald-400" />
          ) : (
            <XCircle className="size-4 text-red-400" />
          );
        },
      },
      {
        id: "confidence",
        header: () => (
          <span className="text-[10px] uppercase tracking-wider text-muted-foreground">
            Confidence
          </span>
        ),
        accessorFn: (row) => row.anzsco_assessment?.confidence_score,
        cell: ({ row }) => {
          const score = row.original.anzsco_assessment?.confidence_score;
          if (score == null)
            return <span className="text-muted-foreground/50">--</span>;
          const percent = Math.round(score * 100);
          return (
            <span
              className={`font-[family-name:var(--font-heading)] text-sm font-semibold tracking-tight ${getConfidenceColor(
                score
              )}`}
            >
              {percent}%
            </span>
          );
        },
      },
      {
        id: "actions",
        header: "",
        cell: ({ row }) => (
          <Button
            variant="ghost"
            size="icon-sm"
            onClick={(e) => {
              e.stopPropagation();
              setSelectedJob(row.original);
            }}
            className="text-muted-foreground hover:text-primary hover:bg-primary/10 transition-colors"
          >
            <Eye className="size-4" />
          </Button>
        ),
      },
    ],
    []
  );

  const table = useReactTable({
    data: jobs,
    columns,
    state: { sorting },
    onSortingChange: setSorting,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
  });

  if (jobs.length === 0) {
    return (
      <div className="py-12 text-center">
        <p className="text-sm text-muted-foreground">No jobs to display.</p>
      </div>
    );
  }

  return (
    <>
      <div className="rounded-lg border border-border/50 overflow-hidden">
        <Table>
          <TableHeader>
            {table.getHeaderGroups().map((headerGroup) => (
              <TableRow key={headerGroup.id} className="border-border/50 bg-background/30 hover:bg-background/30">
                {headerGroup.headers.map((header) => (
                  <TableHead key={header.id} className="h-9">
                    {header.isPlaceholder
                      ? null
                      : flexRender(
                          header.column.columnDef.header,
                          header.getContext()
                        )}
                  </TableHead>
                ))}
              </TableRow>
            ))}
          </TableHeader>
          <TableBody>
            {table.getRowModel().rows.map((row) => (
              <TableRow
                key={row.id}
                className="cursor-pointer border-border/30 hover:bg-primary/5 transition-colors"
                onClick={() => setSelectedJob(row.original)}
              >
                {row.getVisibleCells().map((cell) => (
                  <TableCell key={cell.id} className="py-3">
                    {flexRender(cell.column.columnDef.cell, cell.getContext())}
                  </TableCell>
                ))}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>

      <JobDetailSheet
        job={selectedJob}
        open={selectedJob !== null}
        onOpenChange={(open) => {
          if (!open) setSelectedJob(null);
        }}
      />
    </>
  );
}
