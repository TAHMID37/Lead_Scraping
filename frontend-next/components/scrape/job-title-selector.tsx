"use client";

import { useState } from "react";
import { JOB_TITLES } from "@/lib/constants";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Command,
  CommandInput,
  CommandList,
  CommandEmpty,
  CommandGroup,
  CommandItem,
} from "@/components/ui/command";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog";
import { ChevronsUpDown, X, Check } from "lucide-react";

interface JobTitleSelectorProps {
  selected: string[];
  onChange: (titles: string[]) => void;
}

export function JobTitleSelector({ selected, onChange }: JobTitleSelectorProps) {
  const [open, setOpen] = useState(false);

  function toggleTitle(title: string) {
    if (selected.includes(title)) {
      onChange(selected.filter((t) => t !== title));
    } else {
      onChange([...selected, title]);
    }
  }

  function removeTitle(title: string) {
    onChange(selected.filter((t) => t !== title));
  }

  return (
    <div className="space-y-2">
      <Button
        type="button"
        variant="outline"
        onClick={() => setOpen(true)}
        className="w-full justify-between bg-background/50 border-border/50 hover:bg-accent/50 hover:border-primary/30 transition-colors"
      >
        <span className={selected.length === 0 ? "text-muted-foreground" : ""}>
          {selected.length === 0
            ? "Select job titles..."
            : `${selected.length} title${selected.length === 1 ? "" : "s"} selected`}
        </span>
        <ChevronsUpDown className="ml-2 size-4 text-muted-foreground" />
      </Button>

      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent className="sm:max-w-lg p-0 border-border/50 bg-card overflow-hidden" showCloseButton={false}>
          <DialogHeader className="sr-only">
            <DialogTitle>Select Job Titles</DialogTitle>
            <DialogDescription>Search and select ANZSCO job titles</DialogDescription>
          </DialogHeader>
          <Command className="bg-transparent">
            <div className="border-b border-border/50 px-1">
              <CommandInput
                placeholder="Search ANZSCO job titles..."
                className="h-11"
              />
            </div>
            <CommandList className="max-h-72 scrollbar-thin">
              <CommandEmpty className="py-6 text-center text-sm text-muted-foreground">
                No job titles found.
              </CommandEmpty>
              <CommandGroup>
                {JOB_TITLES.map((title) => {
                  const isSelected = selected.includes(title);
                  return (
                    <CommandItem
                      key={title}
                      value={title}
                      onSelect={() => toggleTitle(title)}
                      className={`flex items-center gap-2 cursor-pointer ${
                        isSelected
                          ? "bg-primary/10 text-primary"
                          : "hover:bg-accent/50"
                      }`}
                    >
                      <div
                        className={`flex size-4 shrink-0 items-center justify-center rounded border transition-colors ${
                          isSelected
                            ? "border-primary bg-primary text-primary-foreground"
                            : "border-border/80"
                        }`}
                      >
                        {isSelected && <Check className="size-3" />}
                      </div>
                      <span className="flex-1 text-sm">{title}</span>
                    </CommandItem>
                  );
                })}
              </CommandGroup>
            </CommandList>
          </Command>
          <DialogFooter className="border-t border-border/50 px-4 py-3 bg-background/30">
            <div className="flex w-full items-center justify-between">
              <span className="text-xs text-muted-foreground">
                {selected.length} selected
              </span>
              <div className="flex gap-2">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => onChange([])}
                  className="text-xs text-muted-foreground hover:text-foreground"
                >
                  Clear All
                </Button>
                <Button
                  size="sm"
                  onClick={() => setOpen(false)}
                  className="bg-primary hover:bg-primary/90 text-primary-foreground font-[family-name:var(--font-heading)] text-xs tracking-wider"
                >
                  Done ({selected.length})
                </Button>
              </div>
            </div>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {selected.length > 0 && (
        <div className="flex flex-wrap gap-1.5">
          {selected.map((title) => (
            <Badge
              key={title}
              variant="secondary"
              className="gap-1 bg-primary/10 text-primary border border-primary/20 hover:bg-primary/15 transition-colors"
            >
              <span className="text-xs">{title}</span>
              <button
                type="button"
                onClick={() => removeTitle(title)}
                className="ml-0.5 rounded-full p-0.5 hover:bg-primary/20 transition-colors"
              >
                <X className="size-3" />
              </button>
            </Badge>
          ))}
        </div>
      )}
    </div>
  );
}
