"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { apiClient } from "@/lib/api-client";
import { LoadingSpinner } from "@/components/ui/LoadingSpinner";
import { ErrorBoundary } from "@/components/ui/ErrorBoundary";
import type { Project, Dataset } from "@/types";

export default function ProjectsPage() {
  const router = useRouter();
  const [projects, setProjects] = useState<Project[]>([]);
  const [datasets, setDatasets] = useState<Record<string, Dataset>>({});
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [deletingId, setDeletingId] = useState<string | null>(null);

  useEffect(() => {
    loadProjects();
    loadDatasets();
  }, []);

  const loadProjects = async () => {
    try {
      setIsLoading(true);
      const data = await apiClient.get<Project[]>("/projects/");
      setProjects(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load projects");
    } finally {
      setIsLoading(false);
    }
  };

  const loadDatasets = async () => {
    try {
      const data = await apiClient.get<Dataset[]>("/datasets/");
      const datasetMap: Record<string, Dataset> = {};
      data.forEach((ds) => {
        datasetMap[ds.id] = ds;
      });
      setDatasets(datasetMap);
    } catch (err) {
      console.error("Failed to load datasets:", err);
    }
  };

  const handleDelete = async (projectId: string, projectName: string, e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    
    if (!confirm(`Are you sure you want to delete "${projectName}"? This action cannot be undone.`)) {
      return;
    }

    try {
      setDeletingId(projectId);
      await apiClient.delete(`/projects/${projectId}`);
      await loadProjects();
    } catch (err) {
      alert(err instanceof Error ? err.message : "Failed to delete project");
    } finally {
      setDeletingId(null);
    }
  };

  const filteredProjects = projects.filter((project) =>
    project.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    (project.description && project.description.toLowerCase().includes(searchQuery.toLowerCase()))
  );

  const getProjectStatus = (project: Project) => {
    if (project.model_id) {
      return { label: "Model Trained", color: "green", icon: "✓" };
    }
    if (project.dataset_id) {
      return { label: "Dataset Ready", color: "blue", icon: "📊" };
    }
    return { label: "New", color: "gray", icon: "○" };
  };

  return (
    <ErrorBoundary>
      <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800">
        <div className="container mx-auto px-4 py-8">
          {/* Header */}
          <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4">
            <div>
              <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">Projects</h1>
              <p className="text-gray-600 dark:text-gray-400">
                Manage your time series analysis projects
              </p>
            </div>
            <Link
              href="/projects/new"
              className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 font-medium shadow-md transition-colors flex items-center gap-2"
            >
              <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
              New Project
            </Link>
          </div>

          {/* Search Bar */}
          {projects.length > 0 && (
            <div className="mb-6">
              <div className="relative max-w-md">
                <input
                  type="text"
                  placeholder="Search projects..."
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
            </div>
          )}

          {/* Content */}
          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <LoadingSpinner message="Loading projects..." />
            </div>
          ) : error ? (
            <div className="p-4 bg-red-50 dark:bg-red-900 border border-red-200 dark:border-red-700 rounded-lg text-red-700 dark:text-red-200">
              <div className="flex items-center justify-between">
                <span>{error}</span>
                <button
                  onClick={loadProjects}
                  className="px-3 py-1 bg-red-600 text-white rounded text-sm hover:bg-red-700"
                >
                  Retry
                </button>
              </div>
            </div>
          ) : projects.length === 0 ? (
            <div className="text-center py-16 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700">
              <div className="text-gray-400 dark:text-gray-500 mb-4">
                <svg className="mx-auto h-16 w-16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <p className="text-gray-600 dark:text-gray-400 text-lg font-medium mb-2">No projects yet</p>
              <p className="text-gray-500 dark:text-gray-500 text-sm mb-6">
                Create a project to start analyzing your time series data
              </p>
              <Link
                href="/projects/new"
                className="inline-block px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 font-medium"
              >
                Create Your First Project
              </Link>
            </div>
          ) : filteredProjects.length === 0 ? (
            <div className="text-center py-12 text-gray-500 dark:text-gray-400">
              No projects match your search.
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredProjects.map((project) => {
                const status = getProjectStatus(project);
                const dataset = project.dataset_id ? datasets[project.dataset_id] : null;
                
                return (
                  <div
                    key={project.id}
                    className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-sm hover:shadow-lg transition-shadow p-6 relative group"
                  >
                    {/* Delete Button */}
                    <button
                      onClick={(e) => handleDelete(project.id, project.name, e)}
                      disabled={deletingId === project.id}
                      className="absolute top-4 right-4 p-2 text-gray-400 hover:text-red-600 dark:hover:text-red-400 opacity-0 group-hover:opacity-100 transition-opacity disabled:opacity-50"
                      title="Delete project"
                    >
                      {deletingId === project.id ? (
                        <svg className="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
                          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                        </svg>
                      ) : (
                        <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
                      )}
                    </button>

                    {/* Status Badge */}
                    <div className="mb-4">
                      <span
                        className={`inline-flex items-center gap-1 px-2.5 py-1 text-xs font-medium rounded-full ${
                          status.color === "green"
                            ? "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200"
                            : status.color === "blue"
                            ? "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200"
                            : "bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300"
                        }`}
                      >
                        <span>{status.icon}</span>
                        {status.label}
                      </span>
                    </div>

                    {/* Project Name */}
                    <Link href={`/projects/${project.id}`}>
                      <h3 className="text-xl font-semibold mb-2 text-gray-900 dark:text-white hover:text-green-600 dark:hover:text-green-400 transition-colors">
                        {project.name}
                      </h3>
                    </Link>

                    {/* Description */}
                    {project.description && (
                      <p className="text-gray-600 dark:text-gray-400 text-sm mb-4 line-clamp-2">
                        {project.description}
                      </p>
                    )}

                    {/* Dataset Info */}
                    {dataset && (
                      <div className="mb-4 p-3 bg-gray-50 dark:bg-gray-700 rounded-md">
                        <div className="flex items-center gap-2 mb-1">
                          <svg className="h-4 w-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                          </svg>
                          <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                            {dataset.name}
                          </span>
                        </div>
                        <p className="text-xs text-gray-500 dark:text-gray-400">
                          {dataset.row_count.toLocaleString()} rows • {dataset.columns.length} columns
                        </p>
                      </div>
                    )}

                    {/* Actions */}
                    <div className="flex items-center justify-between pt-4 border-t border-gray-200 dark:border-gray-700">
                      <div className="text-xs text-gray-500 dark:text-gray-400">
                        {new Date(project.created_at).toLocaleDateString("en-US", {
                          year: "numeric",
                          month: "short",
                          day: "numeric",
                        })}
                      </div>
                      <Link
                        href={`/projects/${project.id}`}
                        className="px-4 py-2 text-sm font-medium bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors"
                      >
                        {project.model_id ? "View Results" : project.dataset_id ? "Start Analysis" : "Configure"}
                      </Link>
                    </div>
                  </div>
                );
              })}
            </div>
          )}

          {/* Results Count */}
          {searchQuery && filteredProjects.length > 0 && (
            <p className="mt-4 text-sm text-gray-500 dark:text-gray-400 text-center">
              Showing {filteredProjects.length} of {projects.length} project{projects.length !== 1 ? "s" : ""}
            </p>
          )}
        </div>
      </div>
    </ErrorBoundary>
  );
}
