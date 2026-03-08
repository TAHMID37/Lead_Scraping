"use client";

import { useState } from "react";
import { useApiKeys } from "@/lib/api-keys";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import {
  Eye,
  EyeOff,
  Pencil,
  Trash2,
  Save,
  X,
  Shield,
  Key,
  CheckCircle2,
  AlertCircle,
  Info,
} from "lucide-react";

function maskKey(key: string): string {
  if (!key) return "";
  if (key.length <= 8) return "****";
  return key.slice(0, 4) + " **** " + key.slice(-4);
}

interface ApiKeyCardProps {
  name: string;
  description: string;
  value: string;
  isEditing: boolean;
  editValue: string;
  onEditValueChange: (val: string) => void;
  onStartEdit: () => void;
  onSave: () => void;
  onCancel: () => void;
  required?: boolean;
}

function ApiKeyCard({
  name,
  description,
  value,
  isEditing,
  editValue,
  onEditValueChange,
  onStartEdit,
  onSave,
  onCancel,
  required,
}: ApiKeyCardProps) {
  const [showValue, setShowValue] = useState(false);
  const isConfigured = !!value;

  return (
    <Card className="border-border/50">
      <CardContent className="pt-6">
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1 min-w-0 space-y-3">
            {/* Header row */}
            <div className="flex items-center gap-2.5">
              <div className="flex size-8 items-center justify-center rounded-md bg-secondary/60">
                <Key className="size-4 text-muted-foreground" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h3 className="text-sm font-semibold text-foreground">
                    {name}
                  </h3>
                  {required && (
                    <span className="rounded border border-primary/30 bg-primary/10 px-1.5 py-0 text-[10px] font-medium uppercase tracking-wider text-primary">
                      Required
                    </span>
                  )}
                </div>
                <p className="text-xs text-muted-foreground">{description}</p>
              </div>
            </div>

            {/* Status / value */}
            {isEditing ? (
              <div className="flex items-center gap-2">
                <div className="relative flex-1">
                  <Input
                    type={showValue ? "text" : "password"}
                    value={editValue}
                    onChange={(e) => onEditValueChange(e.target.value)}
                    placeholder={`Enter ${name}`}
                    className="pr-10 bg-secondary/30 border-border/50 font-mono text-sm"
                    autoFocus
                  />
                  <button
                    type="button"
                    onClick={() => setShowValue(!showValue)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground transition-colors hover:text-foreground"
                  >
                    {showValue ? (
                      <EyeOff className="size-4" />
                    ) : (
                      <Eye className="size-4" />
                    )}
                  </button>
                </div>
                <Button size="sm" onClick={onSave} className="gap-1">
                  <Save className="size-3.5" />
                  Save
                </Button>
                <Button size="sm" variant="ghost" onClick={onCancel}>
                  <X className="size-3.5" />
                </Button>
              </div>
            ) : (
              <div className="flex items-center gap-3">
                {isConfigured ? (
                  <div className="flex items-center gap-2">
                    <CheckCircle2 className="size-3.5 text-emerald-400" />
                    <span className="font-mono text-sm text-muted-foreground">
                      {maskKey(value)}
                    </span>
                  </div>
                ) : (
                  <div className="flex items-center gap-2">
                    <AlertCircle className="size-3.5 text-muted-foreground/50" />
                    <span className="text-sm text-muted-foreground/50 italic">
                      Not configured
                    </span>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Edit button */}
          {!isEditing && (
            <Button
              variant="outline"
              size="sm"
              onClick={onStartEdit}
              className="shrink-0 gap-1.5 border-border/50"
            >
              <Pencil className="size-3" />
              Edit
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

export default function SettingsPage() {
  const { keys, setKeys, clearKeys } = useApiKeys();
  const router = useRouter();

  const [editing, setEditing] = useState<string | null>(null);
  const [editValue, setEditValue] = useState("");

  function startEdit(field: string, currentValue: string) {
    setEditing(field);
    setEditValue(currentValue);
  }

  function saveField(field: string) {
    const newKeys = { ...keys, [field]: editValue.trim() };
    setKeys(newKeys);
    setEditing(null);
    setEditValue("");
    toast.success("API key updated");
  }

  function cancelEdit() {
    setEditing(null);
    setEditValue("");
  }

  function handleClearAll() {
    clearKeys();
    toast.success("All API keys cleared");
    router.push("/setup");
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="font-[family-name:var(--font-heading)] text-3xl font-bold tracking-tight">
          Settings
        </h1>
        <p className="mt-1 text-muted-foreground">
          Manage your API keys and configuration
        </p>
      </div>

      {/* Storage notice */}
      <div className="flex items-start gap-2.5 rounded-lg border border-primary/20 bg-primary/5 px-4 py-3">
        <Info className="mt-0.5 size-4 shrink-0 text-primary" />
        <p className="text-sm text-primary/80">
          Keys are stored in your browser&apos;s session storage only. They are
          never sent to any third-party server and will be cleared when you close
          the tab.
        </p>
      </div>

      {/* API Key Cards */}
      <div className="space-y-4">
        <h2 className="font-[family-name:var(--font-heading)] text-lg font-semibold tracking-tight flex items-center gap-2">
          <Shield className="size-4 text-primary" />
          API Keys
        </h2>

        <div className="space-y-3">
          <ApiKeyCard
            name="Spider API Key"
            description="Required for web scraping via Spider.cloud"
            value={keys.spiderApiKey}
            isEditing={editing === "spiderApiKey"}
            editValue={editValue}
            onEditValueChange={setEditValue}
            onStartEdit={() => startEdit("spiderApiKey", keys.spiderApiKey)}
            onSave={() => saveField("spiderApiKey")}
            onCancel={cancelEdit}
            required
          />

          <ApiKeyCard
            name="Gemini API Key"
            description="Required for AI-powered ANZSCO occupation validation"
            value={keys.geminiApiKey}
            isEditing={editing === "geminiApiKey"}
            editValue={editValue}
            onEditValueChange={setEditValue}
            onStartEdit={() => startEdit("geminiApiKey", keys.geminiApiKey)}
            onSave={() => saveField("geminiApiKey")}
            onCancel={cancelEdit}
            required
          />

          <ApiKeyCard
            name="HubSpot API Key"
            description="Optional. Used for syncing discovered companies to HubSpot CRM"
            value={keys.hubspotApiKey}
            isEditing={editing === "hubspotApiKey"}
            editValue={editValue}
            onEditValueChange={setEditValue}
            onStartEdit={() => startEdit("hubspotApiKey", keys.hubspotApiKey)}
            onSave={() => saveField("hubspotApiKey")}
            onCancel={cancelEdit}
          />
        </div>
      </div>

      {/* Danger Zone */}
      <div className="space-y-4">
        <Separator className="bg-border/50" />

        <Card className="border-red-500/20">
          <CardHeader>
            <CardTitle className="font-[family-name:var(--font-heading)] text-lg tracking-tight text-red-400">
              Danger Zone
            </CardTitle>
            <CardDescription>
              Irreversible actions that affect your stored configuration
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between gap-4">
              <div>
                <p className="text-sm font-medium text-foreground">
                  Clear all API keys
                </p>
                <p className="text-xs text-muted-foreground">
                  This will remove all stored keys and redirect you to the setup
                  page.
                </p>
              </div>
              <Button
                variant="destructive"
                size="sm"
                onClick={handleClearAll}
                className="shrink-0 gap-1.5"
              >
                <Trash2 className="size-3.5" />
                Clear All Keys
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
