"use client";

import React, { useEffect, useState } from "react";
import { apiClient } from "../../lib/api-client";
import { Dataset } from "../../types";
import { LoadingSpinner } from "../ui/LoadingSpinner";

interface DatasetListProps {
  onSelectDataset: (dataset: Dataset) => void;
  refreshKey?: number;
}

export function DatasetList({ onSelectDataset, refreshKey = 0 }: DatasetListProps) {
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const [viewDetailsId, setViewDetailsId] = useState<string | null>(null);

  const loadDatasets = async () => {
    try {
      setLoading(true);
      const data = await apiClient.get<Dataset[]>("/datasets/");
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
  }, [refreshKey]);

  const handleDelete = async (datasetId: string, datasetName: string) => {
    if (!confirm(`Are you sure you want to delete "${datasetName}"? This action cannot be undone.`)) {
      return;
    }

    try {
      setDeletingId(datasetId);
      await apiClient.delete(`/datasets/${datasetId}`);
      // Reload datasets after deletion
      await loadDatasets();
    } catch (err) {
      alert(err instanceof Error ? err.message : "Failed to delete dataset");
    } finally {
      setDeletingId(null);
    }
  };

  const filteredDatasets = datasets.filter((dataset) =>
    dataset.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    dataset.filename.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const isSampleDataset = (dataset: Dataset) => {
    return dataset.name.toLowerCase().startsWith("sample:");
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <LoadingSpinner message="Loading datasets..." />
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4 bg-red-50 dark:bg-red-900 border border-red-200 dark:border-red-700 rounded-md text-red-700 dark:text-red-200">
        <div className="flex items-center justify-between">
          <span>{error}</span>
          <button
            onClick={loadDatasets}
            className="px-3 py-1 bg-red-600 text-white rounded text-sm hover:bg-red-700"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (datasets.length === 0) {
    return (
      <div className="text-center py-12">
        <div className="text-gray-400 dark:text-gray-500 mb-4">
          <svg
            className="mx-auto h-16 w-16"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={1.5}
              d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
            />
          </svg>
        </div>
        <p className="text-gray-500 dark:text-gray-400 text-lg font-medium mb-2">
          No datasets yet
        </p>
        <p className="text-gray-400 dark:text-gray-500 text-sm">
          Upload a file or load a sample dataset to get started.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Search Bar */}
      <div className="relative">
        <input
          type="text"
          placeholder="Search datasets by name or filename..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="w-full px-4 py-2 pl-10 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 dark:bg-gray-700 dark:text-white"
        />
        <svg
          className="absolute left-3 top-2.5 h-5 w-5 text-gray-400"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
          />
        </svg>
        {searchQuery && (
          <button
            onClick={() => setSearchQuery("")}
            className="absolute right-3 top-2.5 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
          >
            <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        )}
      </div>

      {/* Results Count */}
      {searchQuery && (
        <p className="text-sm text-gray-500 dark:text-gray-400">
          {filteredDatasets.length} of {datasets.length} dataset{datasets.length !== 1 ? "s" : ""} found
        </p>
      )}

      {/* Dataset Grid */}
      {filteredDatasets.length === 0 ? (
        <div className="text-center py-8 text-gray-500 dark:text-gray-400">
          No datasets match your search.
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {filteredDatasets.map((dataset) => (
            <div
              key={dataset.id}
              className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-sm hover:shadow-md transition-shadow p-5"
            >
              {/* Header */}
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <h3 className="font-semibold text-gray-900 dark:text-white truncate">
                      {dataset.name}
                    </h3>
                    {isSampleDataset(dataset) && (
                      <span className="px-2 py-0.5 text-xs font-medium bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 rounded">
                        Sample
                      </span>
                    )}
                  </div>
                  <p className="text-xs text-gray-500 dark:text-gray-400 truncate">
                    {dataset.filename}
                  </p>
                </div>
              </div>

              {/* Stats */}
              <div className="grid grid-cols-2 gap-3 mb-4">
                <div className="flex items-center gap-2">
                  <svg
                    className="h-4 w-4 text-gray-400"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
                    />
                  </svg>
                  <span className="text-sm text-gray-600 dark:text-gray-300">
                    {dataset.row_count.toLocaleString()} rows
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <svg
                    className="h-4 w-4 text-gray-400"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4"
                    />
                  </svg>
                  <span className="text-sm text-gray-600 dark:text-gray-300">
                    {dataset.columns.length} columns
                  </span>
                </div>
              </div>

              {/* Columns Preview */}
              {viewDetailsId === dataset.id ? (
                <div className="mb-4 p-3 bg-gray-50 dark:bg-gray-700 rounded-md">
                  <p className="text-xs font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Columns:
                  </p>
                  <div className="flex flex-wrap gap-1">
                    {dataset.columns.slice(0, 8).map((col, idx) => (
                      <span
                        key={idx}
                        className="px-2 py-1 text-xs bg-white dark:bg-gray-600 text-gray-700 dark:text-gray-300 rounded border border-gray-200 dark:border-gray-500"
                      >
                        {col}
                      </span>
                    ))}
                    {dataset.columns.length > 8 && (
                      <span className="px-2 py-1 text-xs text-gray-500 dark:text-gray-400">
                        +{dataset.columns.length - 8} more
                      </span>
                    )}
                  </div>
                </div>
              ) : null}

              {/* Footer */}
              <div className="flex items-center justify-between pt-3 border-t border-gray-200 dark:border-gray-700">
                <div className="text-xs text-gray-500 dark:text-gray-400">
                  {new Date(dataset.created_at).toLocaleDateString("en-US", {
                    year: "numeric",
                    month: "short",
                    day: "numeric",
                  })}
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() =>
                      setViewDetailsId(viewDetailsId === dataset.id ? null : dataset.id)
                    }
                    className="px-3 py-1.5 text-xs font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded transition-colors"
                    title="View details"
                  >
                    {viewDetailsId === dataset.id ? "Hide" : "Details"}
                  </button>
                  <button
                    onClick={() => onSelectDataset(dataset)}
                    className="px-3 py-1.5 text-xs font-medium bg-green-600 text-white rounded hover:bg-green-700 transition-colors"
                  >
                    Use
                  </button>
                  <button
                    onClick={() => handleDelete(dataset.id, dataset.name)}
                    disabled={deletingId === dataset.id}
                    className="px-3 py-1.5 text-xs font-medium text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900 rounded transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    title="Delete dataset"
                  >
                    {deletingId === dataset.id ? (
                      <span className="flex items-center gap-1">
                        <svg
                          className="animate-spin h-3 w-3"
                          fill="none"
                          viewBox="0 0 24 24"
                        >
                          <circle
                            className="opacity-25"
                            cx="12"
                            cy="12"
                            r="10"
                            stroke="currentColor"
                            strokeWidth="4"
                          />
                          <path
                            className="opacity-75"
                            fill="currentColor"
                            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                          />
                        </svg>
                        Deleting...
                      </span>
                    ) : (
                      <svg
                        className="h-4 w-4"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                        />
                      </svg>
                    )}
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

