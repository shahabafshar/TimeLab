"use client";

import React, { useEffect, useState } from "react";
import { apiClient } from "../../lib/api-client";
import { LoadingSpinner } from "../ui/LoadingSpinner";

interface SampleDataset {
  filename: string;
  name: string;
  description: string;
  frequency: string;
  rows: number;
  columns: string[];
}

interface SampleDatasetLoaderProps {
  onLoadSuccess: () => void;
}

export function SampleDatasetLoader({ onLoadSuccess }: SampleDatasetLoaderProps) {
  const [samples, setSamples] = useState<SampleDataset[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadingDataset, setLoadingDataset] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadSamples();
  }, []);

  const loadSamples = async () => {
    try {
      setLoading(true);
      const data = await apiClient.get<SampleDataset[]>("/api/v1/datasets/samples");
      setSamples(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load sample datasets");
    } finally {
      setLoading(false);
    }
  };

  const handleLoadSample = async (filename: string) => {
    try {
      setLoadingDataset(filename);
      setError(null);
      
      await apiClient.post("/api/v1/datasets/samples/load", { filename });
      
      onLoadSuccess();
      alert(`Sample dataset loaded successfully!`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load sample dataset");
    } finally {
      setLoadingDataset(null);
    }
  };

  if (loading) {
    return <LoadingSpinner message="Loading sample datasets..." />;
  }

  if (error) {
    return (
      <div className="p-4 bg-red-50 dark:bg-red-900 border border-red-200 dark:border-red-700 rounded-md text-red-700 dark:text-red-200">
        {error}
      </div>
    );
  }

  if (samples.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500 dark:text-gray-400">
        No sample datasets available
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
          Load Sample Dataset
        </h3>
        <p className="text-sm text-gray-600 dark:text-gray-400">
          Choose a well-known time series dataset to get started quickly
        </p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {samples.map((sample) => (
          <div
            key={sample.filename}
            className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
          >
            <div className="flex justify-between items-start mb-2">
              <div className="flex-1">
                <h4 className="font-semibold text-gray-900 dark:text-white">
                  {sample.name}
                </h4>
                <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                  {sample.description}
                </p>
                <div className="flex gap-4 mt-2 text-xs text-gray-500 dark:text-gray-500">
                  <span>{sample.rows} rows</span>
                  <span>{sample.frequency}</span>
                </div>
              </div>
              <button
                onClick={() => handleLoadSample(sample.filename)}
                disabled={loadingDataset === sample.filename}
                className="ml-4 px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed text-sm whitespace-nowrap"
              >
                {loadingDataset === sample.filename ? "Loading..." : "Load"}
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

