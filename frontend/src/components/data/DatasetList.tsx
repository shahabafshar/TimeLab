"use client";

import React, { useEffect, useState } from "react";
import { apiClient } from "../../lib/api-client";
import { Dataset } from "../../types";
import { LoadingSpinner } from "../ui/LoadingSpinner";

interface DatasetListProps {
  onSelectDataset: (dataset: Dataset) => void;
}

export function DatasetList({ onSelectDataset }: DatasetListProps) {
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

  if (loading) {
    return <LoadingSpinner message="Loading datasets..." />;
  }

  if (error) {
    return (
      <div className="p-4 bg-red-50 border border-red-200 rounded-md text-red-700">
        {error}
      </div>
    );
  }

  if (datasets.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        No datasets yet. Upload a file to get started.
      </div>
    );
  }

  return (
    <div className="space-y-2">
      {datasets.map((dataset) => (
        <div
          key={dataset.id}
          onClick={() => onSelectDataset(dataset)}
          className="p-4 border rounded-lg hover:bg-gray-50 cursor-pointer transition-colors"
        >
          <div className="flex justify-between items-start">
            <div>
              <h3 className="font-semibold">{dataset.name}</h3>
              <p className="text-sm text-gray-500">
                {dataset.row_count} rows • {dataset.columns.length} columns
              </p>
              <p className="text-xs text-gray-400 mt-1">
                {new Date(dataset.created_at).toLocaleDateString()}
              </p>
            </div>
            <button className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 text-sm">
              Use Dataset
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}

