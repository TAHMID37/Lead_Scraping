import axios from "axios";
import type { ApiKeys } from "./api-keys";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:3001";

export function createApiClient(keys: ApiKeys) {
  const client = axios.create({
    baseURL: API_BASE_URL,
  });

  // Use interceptor to inject latest keys on every request
  client.interceptors.request.use((config) => {
    config.headers["Content-Type"] = "application/json";
    if (keys.spiderApiKey) config.headers["X-Spider-Api-Key"] = keys.spiderApiKey;
    if (keys.geminiApiKey) config.headers["X-Gemini-Api-Key"] = keys.geminiApiKey;
    if (keys.hubspotApiKey) config.headers["X-Hubspot-Api-Key"] = keys.hubspotApiKey;
    return config;
  });

  return client;
}
