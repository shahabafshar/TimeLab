"use client";

import React, { useState, useEffect } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { apiClient } from "../../../src/lib/api-client";
import { Dataset } from "../../../src/types";
import { LoadingSpinner } from "../../../src/components/ui/LoadingSpinner";

export default function NewProjectPage() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const datasetId = searchParams.get("dataset");

  const [dataset, setDataset] = useState<Dataset | null>(null);
  const [loading, setLoading] = useState(true);
  const [projectName, setProjectName] = useState("");
  const [dateColumn, setDateColumn] = useState("");
  const [targetColumn, setTargetColumn] = useState("");
  const [frequency, setFrequency] = useState("Monthly");
  const [creating, setCreating] = useState(false);

  useEffect(() => {
    if (datasetId) {
      loadDataset();
    } else {
      setLoading(false);
    }
  }, [datasetId]);

  const loadDataset = async () => {
    try {
      const data = await apiClient.get<Dataset>(`/datasets/${datasetId}`);
      setDataset(data);
      if (data.columns.length > 0) {
        setDateColumn(data.columns[0]);
        setTargetColumn(data.columns[1] || data.columns[0]);
      }
    } catch (err) {
      console.error("Failed to load dataset:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateProject = async () => {
    if (!dataset || !projectName || !dateColumn || !targetColumn) {
      alert("Please fill in all fields");
      return;
    }

    setCreating(true);
    try {
      // Create project
      const project = await apiClient.post("/projects/", {
        name: projectName,
        dataset_id: dataset.id,
      });

      // Navigate to analysis workflow
      router.push(`/projects/${project.id}/analyze?dateColumn=${dateColumn}&targetColumn=${targetColumn}&frequency=${frequency}`);
    } catch (err) {
      alert(err instanceof Error ? err.message : "Failed to create project");
    } finally {
      setCreating(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner message="Loading dataset..." />
      </div>
    );
  }

  if (!dataset) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold mb-4">Dataset not found</h2>
          <a href="/" className="text-blue-600 hover:underline">
            Go back to home
          </a>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4 max-w-2xl">
        <h1 className="text-3xl font-bold mb-8">Create New Project</h1>

        <div className="bg-white rounded-lg shadow-sm p-6 space-y-6">
          <div>
            <label className="block text-sm font-medium mb-2">Project Name</label>
            <input
              type="text"
              value={projectName}
              onChange={(e) => setProjectName(e.target.value)}
              placeholder="My Forecasting Project"
              className="w-full px-4 py-2 border rounded-md"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Dataset</label>
            <div className="p-4 bg-gray-50 rounded-md">
              <p className="font-medium">{dataset.name}</p>
              <p className="text-sm text-gray-500">
                {dataset.row_count} rows • {dataset.columns.length} columns
              </p>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Date Column</label>
            <select
              value={dateColumn}
              onChange={(e) => setDateColumn(e.target.value)}
              className="w-full px-4 py-2 border rounded-md"
            >
              {dataset.columns.map((col) => (
                <option key={col} value={col}>
                  {col}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Target Column</label>
            <select
              value={targetColumn}
              onChange={(e) => setTargetColumn(e.target.value)}
              className="w-full px-4 py-2 border rounded-md"
            >
              {dataset.columns.map((col) => (
                <option key={col} value={col}>
                  {col}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Data Frequency</label>
            <select
              value={frequency}
              onChange={(e) => setFrequency(e.target.value)}
              className="w-full px-4 py-2 border rounded-md"
            >
              <option value="Hourly">Hourly</option>
              <option value="Daily">Daily</option>
              <option value="Monthly">Monthly</option>
              <option value="Quarterly">Quarterly</option>
              <option value="Yearly">Yearly</option>
            </select>
          </div>

          <div className="flex gap-4 pt-4">
            <button
              onClick={() => router.back()}
              className="px-6 py-2 border rounded-md hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              onClick={handleCreateProject}
              disabled={creating || !projectName}
              className="px-6 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {creating ? "Creating..." : "Create Project"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

