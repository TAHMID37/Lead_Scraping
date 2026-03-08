"use client";

import { createContext, useContext, useState, useEffect, ReactNode } from "react";

export interface ApiKeys {
  spiderApiKey: string;
  geminiApiKey: string;
  hubspotApiKey: string;
}

interface ApiKeysContextType {
  keys: ApiKeys;
  setKeys: (keys: ApiKeys) => void;
  isConfigured: boolean;
  clearKeys: () => void;
}

const ApiKeysContext = createContext<ApiKeysContextType | null>(null);

const STORAGE_KEY = "jobscraper_api_keys";

export function ApiKeysProvider({ children }: { children: ReactNode }) {
  const [keys, setKeysState] = useState<ApiKeys>({
    spiderApiKey: "",
    geminiApiKey: "",
    hubspotApiKey: "",
  });
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    const stored = sessionStorage.getItem(STORAGE_KEY);
    if (stored) {
      try {
        setKeysState(JSON.parse(stored));
      } catch {}
    }
    setLoaded(true);
  }, []);

  const setKeys = (newKeys: ApiKeys) => {
    setKeysState(newKeys);
    sessionStorage.setItem(STORAGE_KEY, JSON.stringify(newKeys));
  };

  const clearKeys = () => {
    setKeysState({ spiderApiKey: "", geminiApiKey: "", hubspotApiKey: "" });
    sessionStorage.removeItem(STORAGE_KEY);
  };

  const isConfigured = !!(keys.spiderApiKey && keys.geminiApiKey);

  if (!loaded) return null;

  return (
    <ApiKeysContext.Provider value={{ keys, setKeys, isConfigured, clearKeys }}>
      {children}
    </ApiKeysContext.Provider>
  );
}

export function useApiKeys() {
  const context = useContext(ApiKeysContext);
  if (!context) throw new Error("useApiKeys must be used within ApiKeysProvider");
  return context;
}
