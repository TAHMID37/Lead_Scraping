"use client";

import React, { createContext, useContext, useState, useCallback, useRef, useEffect } from "react";
import { useApi } from "@/hooks/use-api";
import type { Platform, Job, ScrapeSession } from "./types";

export interface ActiveScrape {
  sessionId: string;
  platform: Platform;
  jobTitles: string[];
  location: string;
  status: string; // scraping | validating | enriching | completed | failed
  totalJobs: number;
  eligibleJobs: number;
  error?: string;
  jobs: Job[];
}

interface ScrapeContextValue {
  activeScrapes: ActiveScrape[];
  startScrape: (platform: Platform, jobTitles: string[], location: string, maxPages: number) => Promise<string | null>;
  getActiveScrape: (sessionId: string) => ActiveScrape | undefined;
  clearScrape: (sessionId: string) => void;
  hasActiveScrape: boolean;
}

const ScrapeContext = createContext<ScrapeContextValue | null>(null);

export function ScrapeProvider({ children }: { children: React.ReactNode }) {
  const api = useApi();
  const apiRef = useRef(api);
  apiRef.current = api;
  const [activeScrapes, setActiveScrapes] = useState<ActiveScrape[]>([]);
  const pollIntervalsRef = useRef<Map<string, ReturnType<typeof setInterval>>>(new Map());

  const stopPolling = useCallback((sessionId: string) => {
    const interval = pollIntervalsRef.current.get(sessionId);
    if (interval) {
      clearInterval(interval);
      pollIntervalsRef.current.delete(sessionId);
    }
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      pollIntervalsRef.current.forEach((interval) => clearInterval(interval));
      pollIntervalsRef.current.clear();
    };
  }, []);

  const pollSession = useCallback((sessionId: string) => {
    const interval = setInterval(async () => {
      try {
        const res = await apiRef.current.get(`/api/sessions/${sessionId}`);
        const session: ScrapeSession = res.data;

        setActiveScrapes((prev) =>
          prev.map((s) =>
            s.sessionId === sessionId
              ? {
                  ...s,
                  status: session.status,
                  totalJobs: session.total_jobs ?? 0,
                  eligibleJobs: session.eligible_jobs ?? 0,
                  error: session.error_message,
                  jobs: session.jobs ?? s.jobs,
                }
              : s
          )
        );

        if (session.status === "completed" || session.status === "failed") {
          stopPolling(sessionId);
        }
      } catch {
        // Keep polling on transient errors
      }
    }, 3000);

    pollIntervalsRef.current.set(sessionId, interval);
  }, [stopPolling]);

  const formatLocation = (location: string, platform: Platform): string => {
    switch (platform) {
      case "seek":
        return location.replace(/\s+/g, "-");
      case "careerone":
        return location.split(" ")[0];
      default:
        return location;
    }
  };

  const startScrape = useCallback(
    async (platform: Platform, jobTitles: string[], location: string, maxPages: number) => {
      try {
        const formattedLocation = formatLocation(location, platform);
        const res = await apiRef.current.post(`/api/scrape/${platform}`, {
          job_titles: jobTitles,
          location: formattedLocation,
          max_pages: maxPages,
        });

        const sessionId = res.data.session_id;
        if (!sessionId) return null;

        const newScrape: ActiveScrape = {
          sessionId,
          platform,
          jobTitles,
          location,
          status: "scraping",
          totalJobs: 0,
          eligibleJobs: 0,
          jobs: [],
        };

        setActiveScrapes((prev) => [...prev, newScrape]);
        pollSession(sessionId);

        return sessionId;
      } catch {
        return null;
      }
    },
    [pollSession]
  );

  const getActiveScrape = useCallback(
    (sessionId: string) => activeScrapes.find((s) => s.sessionId === sessionId),
    [activeScrapes]
  );

  const clearScrape = useCallback(
    (sessionId: string) => {
      stopPolling(sessionId);
      setActiveScrapes((prev) => prev.filter((s) => s.sessionId !== sessionId));
    },
    [stopPolling]
  );

  const hasActiveScrape = activeScrapes.some(
    (s) => s.status === "scraping" || s.status === "validating" || s.status === "enriching"
  );

  return (
    <ScrapeContext.Provider
      value={{ activeScrapes, startScrape, getActiveScrape, clearScrape, hasActiveScrape }}
    >
      {children}
    </ScrapeContext.Provider>
  );
}

export function useScrape() {
  const ctx = useContext(ScrapeContext);
  if (!ctx) throw new Error("useScrape must be used within ScrapeProvider");
  return ctx;
}
