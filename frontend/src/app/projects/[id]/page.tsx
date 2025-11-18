"use client";

import React, { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { apiClient } from "@/lib/api-client";
import { LoadingSpinner } from "@/components/ui/LoadingSpinner";
import { ErrorBoundary } from "@/components/ui/ErrorBoundary";
import { WorkflowWizard } from "@/components/workflow/WorkflowWizard";
import { WorkflowStep } from "@/components/workflow/WorkflowStep";
import type { Project, Dataset } from "@/types";

export default function ProjectDetailPage() {
  const params = useParams();
  const router = useRouter();
  const projectId = params.id as string;

  const [project, setProject] = useState<Project | null>(null);
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showWorkflow, setShowWorkflow] = useState(false);

  useEffect(() => {
    loadProject();
    loadDatasets();
  }, [projectId]);

  const loadProject = async () => {
    try {
      const data = await apiClient.get<Project>(`/projects/${projectId}`);
      setProject(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load project");
    } finally {
      setIsLoading(false);
    }
  };

  const loadDatasets = async () => {
    try {
      const data = await apiClient.get<Dataset[]>("/datasets/");
      setDatasets(data);
    } catch (err) {
      console.error("Failed to load datasets:", err);
    }
  };

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <LoadingSpinner message="Loading project..." />
      </div>
    );
  }

  if (error || !project) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="p-4 bg-red-50 dark:bg-red-900 text-red-800 dark:text-red-200 rounded-md">
          {error || "Project not found"}
        </div>
        <Link href="/projects" className="mt-4 inline-block text-green-600 hover:underline">
          ← Back to Projects
        </Link>
      </div>
    );
  }

  return (
    <ErrorBoundary>
      <div className="container mx-auto px-4 py-8">
        <div className="mb-6">
          <Link href="/projects" className="text-green-600 hover:underline mb-4 inline-block">
            ← Back to Projects
          </Link>
          <h1 className="text-3xl font-bold mt-2">{project.name}</h1>
          {project.description && (
            <p className="text-gray-600 dark:text-gray-400 mt-2">{project.description}</p>
          )}
        </div>

        {!showWorkflow ? (
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-8 border border-gray-200 dark:border-gray-700">
            <div className="mb-6">
              <h2 className="text-2xl font-semibold mb-4">Get Started</h2>
              <p className="text-gray-600 dark:text-gray-400 mb-6">
                Start analyzing your time series data with our guided workflow
              </p>
              <button
                onClick={() => setShowWorkflow(true)}
                className="px-6 py-3 bg-green-600 text-white rounded-md hover:bg-green-700 font-medium"
              >
                Start Analysis Workflow
              </button>
            </div>

            {datasets.length > 0 && (
              <div className="mt-8">
                <h3 className="text-lg font-semibold mb-4">Available Datasets</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {datasets.map((dataset) => (
                    <div
                      key={dataset.id}
                      className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg"
                    >
                      <h4 className="font-semibold">{dataset.name}</h4>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        {dataset.row_count} rows, {dataset.columns.length} columns
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-8 border border-gray-200 dark:border-gray-700">
            <button
              onClick={() => setShowWorkflow(false)}
              className="mb-4 text-green-600 hover:underline"
            >
              ← Back
            </button>
            <WorkflowWizard
              steps={[
                {
                  id: "upload",
                  title: "Upload Data",
                  component: (
                    <WorkflowStep title="Upload Dataset" description="Upload your time series data">
                      <p className="text-gray-600 dark:text-gray-400">
                        Go to the home page to upload a dataset, then return here to continue.
                      </p>
                    </WorkflowStep>
                  ),
                },
                {
                  id: "configure",
                  title: "Configure",
                  component: (
                    <WorkflowStep title="Configure Analysis" description="Set up your analysis parameters">
                      <p className="text-gray-600 dark:text-gray-400">
                        Configuration step - coming soon
                      </p>
                    </WorkflowStep>
                  ),
                },
                {
                  id: "analyze",
                  title: "Analyze",
                  component: (
                    <WorkflowStep title="Run Analysis" description="Perform time series analysis">
                      <p className="text-gray-600 dark:text-gray-400">
                        Analysis step - coming soon
                      </p>
                    </WorkflowStep>
                  ),
                },
              ]}
              onComplete={() => {
                setShowWorkflow(false);
                alert("Workflow completed! (Full implementation coming soon)");
              }}
            />
          </div>
        )}
      </div>
    </ErrorBoundary>
  );
}
