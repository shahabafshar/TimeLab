"use client";

import React, { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { apiClient } from "@/lib/api-client";
import { LoadingSpinner } from "@/components/ui/LoadingSpinner";
import { ErrorBoundary } from "@/components/ui/ErrorBoundary";
import type { Project, Dataset } from "@/types";

export default function ProjectDetailPage() {
  const params = useParams();
  const router = useRouter();
  const projectId = params.id as string;

  const [project, setProject] = useState<Project | null>(null);
  const [dataset, setDataset] = useState<Dataset | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadProject();
  }, [projectId]);

  const loadProject = async () => {
    try {
      setIsLoading(true);
      const data = await apiClient.get<Project>(`/projects/${projectId}`);
      setProject(data);
      
      if (data.dataset_id) {
        try {
          const datasetData = await apiClient.get<Dataset>(`/datasets/${data.dataset_id}`);
          setDataset(datasetData);
        } catch (err) {
          console.error("Failed to load dataset:", err);
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load project");
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800">
        <div className="container mx-auto px-4 py-8">
          <LoadingSpinner message="Loading project..." />
        </div>
      </div>
    );
  }

  if (error || !project) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800">
        <div className="container mx-auto px-4 py-8">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 border border-gray-200 dark:border-gray-700">
            <div className="p-4 bg-red-50 dark:bg-red-900 text-red-800 dark:text-red-200 rounded-md mb-4">
              {error || "Project not found"}
            </div>
            <Link href="/projects" className="text-green-600 dark:text-green-400 hover:underline">
              ← Back to Projects
            </Link>
          </div>
        </div>
      </div>
    );
  }

  const hasDataset = !!project.dataset_id;
  const hasModel = !!project.model_id;

  return (
    <ErrorBoundary>
      <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800">
        <div className="container mx-auto px-4 py-8">
          {/* Header */}
          <div className="mb-8">
            <Link href="/projects" className="text-green-600 dark:text-green-400 hover:underline mb-4 inline-block flex items-center gap-2">
              <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              Back to Projects
            </Link>
            <div className="flex items-start justify-between gap-4">
              <div>
                <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">{project.name}</h1>
                {project.description && (
                  <p className="text-gray-600 dark:text-gray-400 text-lg">{project.description}</p>
                )}
                <div className="mt-4 flex items-center gap-4 text-sm text-gray-500 dark:text-gray-400">
                  <span>
                    Created: {new Date(project.created_at).toLocaleDateString("en-US", {
                      year: "numeric",
                      month: "long",
                      day: "numeric",
                    })}
                  </span>
                  {project.updated_at && (
                    <span>
                      Updated: {new Date(project.updated_at).toLocaleDateString("en-US", {
                        year: "numeric",
                        month: "long",
                        day: "numeric",
                      })}
                    </span>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Status Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            {/* Dataset Status */}
            <div className={`bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 border-2 ${
              hasDataset ? "border-green-500" : "border-gray-200 dark:border-gray-700"
            }`}>
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Dataset</h3>
                {hasDataset ? (
                  <span className="px-2 py-1 text-xs font-medium bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200 rounded-full">
                    ✓ Connected
                  </span>
                ) : (
                  <span className="px-2 py-1 text-xs font-medium bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 rounded-full">
                    Not Set
                  </span>
                )}
              </div>
              {dataset ? (
                <div>
                  <p className="text-sm font-medium text-gray-900 dark:text-white mb-1">{dataset.name}</p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    {dataset.row_count.toLocaleString()} rows • {dataset.columns.length} columns
                  </p>
                </div>
              ) : hasDataset ? (
                <p className="text-sm text-gray-500 dark:text-gray-400">Dataset ID: {project.dataset_id}</p>
              ) : (
                <p className="text-sm text-gray-500 dark:text-gray-400">No dataset assigned</p>
              )}
            </div>

            {/* Model Status */}
            <div className={`bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 border-2 ${
              hasModel ? "border-green-500" : "border-gray-200 dark:border-gray-700"
            }`}>
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Model</h3>
                {hasModel ? (
                  <span className="px-2 py-1 text-xs font-medium bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200 rounded-full">
                    ✓ Trained
                  </span>
                ) : (
                  <span className="px-2 py-1 text-xs font-medium bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 rounded-full">
                    Not Trained
                  </span>
                )}
              </div>
              {hasModel ? (
                <p className="text-sm text-gray-500 dark:text-gray-400">Model ID: {project.model_id}</p>
              ) : (
                <p className="text-sm text-gray-500 dark:text-gray-400">No model trained yet</p>
              )}
            </div>

            {/* Analysis Status */}
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 border-2 border-gray-200 dark:border-gray-700">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Status</h3>
                <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                  hasModel
                    ? "bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200"
                    : hasDataset
                    ? "bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200"
                    : "bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400"
                }`}>
                  {hasModel ? "Complete" : hasDataset ? "Ready" : "New"}
                </span>
              </div>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                {hasModel
                  ? "Analysis complete with trained model"
                  : hasDataset
                  ? "Ready to start analysis"
                  : "Configure dataset to begin"}
              </p>
            </div>
          </div>

          {/* Actions */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-8 border border-gray-200 dark:border-gray-700">
            <h2 className="text-2xl font-semibold mb-6 text-gray-900 dark:text-white">Actions</h2>
            
            {!hasDataset ? (
              <div className="space-y-4">
                <p className="text-gray-600 dark:text-gray-400 mb-4">
                  To get started, you need to assign a dataset to this project.
                </p>
                <Link
                  href="/"
                  className="inline-block px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 font-medium"
                >
                  Go to Datasets
                </Link>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Link
                  href={`/projects/${project.id}/analyze?dateColumn=${dataset?.columns[0] || "date"}&targetColumn=${dataset?.columns[1] || "value"}&frequency=Monthly`}
                  className="p-6 border-2 border-green-500 rounded-lg hover:bg-green-50 dark:hover:bg-green-900 transition-colors group"
                >
                  <div className="flex items-center gap-4">
                    <div className="p-3 bg-green-100 dark:bg-green-900 rounded-lg group-hover:bg-green-200 dark:group-hover:bg-green-800 transition-colors">
                      <svg className="h-8 w-8 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                      </svg>
                    </div>
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-1">
                        {hasModel ? "View Analysis" : "Start Analysis"}
                      </h3>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        {hasModel
                          ? "View your analysis results and forecasts"
                          : "Begin time series analysis workflow"}
                      </p>
                    </div>
                  </div>
                </Link>

                <Link
                  href="/"
                  className="p-6 border-2 border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors group"
                >
                  <div className="flex items-center gap-4">
                    <div className="p-3 bg-gray-100 dark:bg-gray-700 rounded-lg group-hover:bg-gray-200 dark:group-hover:bg-gray-600 transition-colors">
                      <svg className="h-8 w-8 text-gray-600 dark:text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                      </svg>
                    </div>
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-1">
                        Manage Datasets
                      </h3>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        Upload or select a different dataset
                      </p>
                    </div>
                  </div>
                </Link>
              </div>
            )}
          </div>
        </div>
      </div>
    </ErrorBoundary>
  );
}
