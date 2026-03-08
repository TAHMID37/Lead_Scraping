"use client";

import { useApiKeys } from "@/lib/api-keys";
import { createApiClient } from "@/lib/api";

export function useApi() {
  const { keys } = useApiKeys();
  // Create fresh client each render to ensure latest keys are used
  return createApiClient(keys);
}
