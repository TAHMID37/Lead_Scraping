"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useApiKeys } from "@/lib/api-keys";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Eye, EyeOff, Zap, Shield } from "lucide-react";
import { toast } from "sonner";

export default function SetupPage() {
  const router = useRouter();
  const { setKeys } = useApiKeys();
  const [spider, setSpider] = useState("");
  const [gemini, setGemini] = useState("");
  const [hubspot, setHubspot] = useState("");
  const [showKeys, setShowKeys] = useState({ spider: false, gemini: false, hubspot: false });

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!spider.trim() || !gemini.trim()) {
      toast.error("Spider and Gemini API keys are required");
      return;
    }
    setKeys({
      spiderApiKey: spider.trim(),
      geminiApiKey: gemini.trim(),
      hubspotApiKey: hubspot.trim(),
    });
    toast.success("System initialized");
    router.push("/");
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-background p-4">
      {/* Background grid effect */}
      <div className="pointer-events-none fixed inset-0 bg-[linear-gradient(oklch(0.25_0.008_260)_1px,transparent_1px),linear-gradient(90deg,oklch(0.25_0.008_260)_1px,transparent_1px)] bg-[size:60px_60px] opacity-20" />

      {/* Radial glow */}
      <div className="pointer-events-none fixed left-1/2 top-1/3 -translate-x-1/2 -translate-y-1/2 size-[600px] rounded-full bg-primary/5 blur-[120px]" />

      <div className="relative z-10 w-full max-w-lg">
        {/* Header */}
        <div className="mb-8 text-center">
          <div className="mb-4 inline-flex items-center gap-2 rounded-full border border-primary/20 bg-primary/5 px-4 py-1.5">
            <Zap className="size-3.5 text-primary" />
            <span className="font-[family-name:var(--font-heading)] text-xs tracking-wider text-primary">
              ANZSCO 482 VALIDATION ENGINE
            </span>
          </div>
          <h1 className="font-[family-name:var(--font-heading)] text-4xl font-bold tracking-tight text-foreground">
            Job<span className="text-primary">Scraper</span>
          </h1>
          <p className="mt-2 text-sm text-muted-foreground">
            Enter your API keys to begin scraping Australian job platforms
          </p>
        </div>

        {/* Card with animated border */}
        <div className="relative rounded-xl p-px bg-gradient-to-b from-primary/20 via-border/50 to-border/50">
          <form onSubmit={handleSubmit} className="rounded-xl bg-card p-6 space-y-5">
            {/* Spider Key */}
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <Label className="text-sm font-medium">Spider API Key</Label>
                <Badge variant="destructive" className="text-[10px] px-1.5 py-0">Required</Badge>
              </div>
              <p className="text-xs text-muted-foreground">Powers web scraping via Spider.cloud</p>
              <div className="relative">
                <Input
                  type={showKeys.spider ? "text" : "password"}
                  value={spider}
                  onChange={(e) => setSpider(e.target.value)}
                  placeholder="sk-..."
                  className="pr-10 bg-background/50 border-border/50 font-[family-name:var(--font-heading)] text-xs"
                />
                <button
                  type="button"
                  onClick={() => setShowKeys(k => ({ ...k, spider: !k.spider }))}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
                >
                  {showKeys.spider ? <EyeOff className="size-3.5" /> : <Eye className="size-3.5" />}
                </button>
              </div>
            </div>

            {/* Gemini Key */}
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <Label className="text-sm font-medium">Gemini API Key</Label>
                <Badge variant="destructive" className="text-[10px] px-1.5 py-0">Required</Badge>
              </div>
              <p className="text-xs text-muted-foreground">AI-powered ANZSCO occupation matching</p>
              <div className="relative">
                <Input
                  type={showKeys.gemini ? "text" : "password"}
                  value={gemini}
                  onChange={(e) => setGemini(e.target.value)}
                  placeholder="AIza..."
                  className="pr-10 bg-background/50 border-border/50 font-[family-name:var(--font-heading)] text-xs"
                />
                <button
                  type="button"
                  onClick={() => setShowKeys(k => ({ ...k, gemini: !k.gemini }))}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
                >
                  {showKeys.gemini ? <EyeOff className="size-3.5" /> : <Eye className="size-3.5" />}
                </button>
              </div>
            </div>

            {/* HubSpot Key */}
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <Label className="text-sm font-medium">HubSpot API Key</Label>
                <Badge variant="secondary" className="text-[10px] px-1.5 py-0">Optional</Badge>
              </div>
              <p className="text-xs text-muted-foreground">Sync discovered companies to HubSpot CRM</p>
              <div className="relative">
                <Input
                  type={showKeys.hubspot ? "text" : "password"}
                  value={hubspot}
                  onChange={(e) => setHubspot(e.target.value)}
                  placeholder="pat-..."
                  className="pr-10 bg-background/50 border-border/50 font-[family-name:var(--font-heading)] text-xs"
                />
                <button
                  type="button"
                  onClick={() => setShowKeys(k => ({ ...k, hubspot: !k.hubspot }))}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
                >
                  {showKeys.hubspot ? <EyeOff className="size-3.5" /> : <Eye className="size-3.5" />}
                </button>
              </div>
            </div>

            <Button type="submit" className="w-full font-[family-name:var(--font-heading)] font-semibold tracking-wide">
              Initialize System
            </Button>
          </form>
        </div>

        {/* Footer */}
        <div className="mt-4 flex items-center justify-center gap-1.5 text-[11px] text-muted-foreground/60">
          <Shield className="size-3" />
          Keys are stored in your browser session only
        </div>
      </div>
    </div>
  );
}
