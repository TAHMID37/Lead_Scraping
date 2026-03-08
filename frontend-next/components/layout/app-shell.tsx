"use client";

import { useApiKeys } from "@/lib/api-keys";
import { usePathname, useRouter } from "next/navigation";
import { useEffect } from "react";
import { Sidebar } from "./sidebar";

export function AppShell({ children }: { children: React.ReactNode }) {
  const { isConfigured } = useApiKeys();
  const pathname = usePathname();
  const router = useRouter();

  useEffect(() => {
    if (!isConfigured && pathname !== "/setup") {
      router.push("/setup");
    }
  }, [isConfigured, pathname, router]);

  if (pathname === "/setup") {
    return <>{children}</>;
  }

  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar />
      <main className="flex-1 overflow-y-auto">
        <div className="mx-auto max-w-7xl px-6 py-8">
          {children}
        </div>
      </main>
    </div>
  );
}
