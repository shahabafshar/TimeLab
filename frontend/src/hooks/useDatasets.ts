"use client";

import { useState, useEffect } from "react";
import { apiClient } from "@/lib/api-client";
import { Dataset } from "@/types";

export function useDatasets() {
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadDatasets = async () => {
    try {
      setLoading(true);
      const data = await apiClient.get<Dataset[]>("/api/v1/datasets/");
      setDatasets(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load datasets");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDatasets();
  }, []);

  return { datasets, loading, error, refresh: loadDatasets };
}

