"use client";

import React, { useState } from "react";
import Link from "next/link";
import { FileUpload } from "../src/components/data/FileUpload";
import { DatasetList } from "../src/components/data/DatasetList";
import { SampleDatasetLoader } from "../src/components/data/SampleDatasetLoader";
import { Dataset } from "../src/types";
import { ErrorBoundary } from "../src/components/ui/ErrorBoundary";

export default function Home() {
  const [activeTab, setActiveTab] = useState<"upload" | "samples" | "datasets">("upload");
  const [refreshKey, setRefreshKey] = useState(0);

  const handleUploadSuccess = () => {
    setActiveTab("datasets");
    setRefreshKey((prev) => prev + 1); // Force refresh of dataset list
  };

  const handleSelectDataset = (dataset: Dataset) => {
    // Navigate to project creation with this dataset
    window.location.href = `/projects/new?dataset=${dataset.id}`;
  };

  return (
    <ErrorBoundary>
      <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800">
        <div className="container mx-auto px-4 py-8">
          {/* Header */}
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">
              TimeLab
            </h1>
            <p className="text-lg text-gray-600 dark:text-gray-300">
              Modern time series forecasting and analysis platform
            </p>
          </div>

          {/* Tabs */}
          <div className="max-w-4xl mx-auto mb-6">
            <div className="flex gap-4 border-b border-gray-200 dark:border-gray-700">
              <button
                onClick={() => setActiveTab("upload")}
                className={`px-6 py-3 font-medium border-b-2 transition-colors ${
                  activeTab === "upload"
                    ? "border-green-600 text-green-600 dark:text-green-400"
                    : "border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400"
                }`}
              >
                Upload Dataset
              </button>
              <button
                onClick={() => setActiveTab("samples")}
                className={`px-6 py-3 font-medium border-b-2 transition-colors ${
                  activeTab === "samples"
                    ? "border-green-600 text-green-600 dark:text-green-400"
                    : "border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400"
                }`}
              >
                Sample Datasets
              </button>
              <button
                onClick={() => setActiveTab("datasets")}
                className={`px-6 py-3 font-medium border-b-2 transition-colors ${
                  activeTab === "datasets"
                    ? "border-green-600 text-green-600 dark:text-green-400"
                    : "border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400"
                }`}
              >
                My Datasets
              </button>
            </div>
          </div>

          {/* Content */}
          <div className="max-w-4xl mx-auto">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-8 border border-gray-200 dark:border-gray-700">
              {activeTab === "upload" && (
                <div className="space-y-6">
                  <div>
                    <h2 className="text-2xl font-semibold mb-2 text-gray-900 dark:text-white">
                      Upload Time Series Data
                    </h2>
                    <p className="text-gray-600 dark:text-gray-400 mb-6">
                      Upload your CSV, Excel, or text file to get started with time series analysis.
                    </p>
                  </div>
                  <FileUpload onUploadSuccess={handleUploadSuccess} />
                  <div className="mt-6 p-4 bg-green-50 dark:bg-green-900 border border-green-200 dark:border-green-700 rounded-md">
                    <h3 className="font-semibold text-green-900 dark:text-green-200 mb-2">
                      Supported Formats
                    </h3>
                    <ul className="text-sm text-green-800 dark:text-green-300 space-y-1">
                      <li>• CSV files (.csv)</li>
                      <li>• Text files (.txt)</li>
                      <li>• Excel files (.xls, .xlsx)</li>
                      <li>• Maximum file size: 50MB</li>
                    </ul>
                  </div>
                </div>
              )}

              {activeTab === "samples" && (
                <div className="space-y-6">
                  <div>
                    <h2 className="text-2xl font-semibold mb-2 text-gray-900 dark:text-white">
                      Sample Datasets
                    </h2>
                    <p className="text-gray-600 dark:text-gray-400 mb-6">
                      Load well-known time series datasets perfect for learning and demonstrations.
                    </p>
                  </div>
                  <SampleDatasetLoader onLoadSuccess={() => {
                    setActiveTab("datasets");
                    setRefreshKey((prev) => prev + 1);
                  }} />
                </div>
              )}

              {activeTab === "datasets" && (
                <div className="space-y-6">
                  <div>
                    <h2 className="text-2xl font-semibold mb-2 text-gray-900 dark:text-white">
                      Your Datasets
                    </h2>
                    <p className="text-gray-600 dark:text-gray-400 mb-6">
                      Select a dataset to create a new forecasting project.
                    </p>
                  </div>
                  <DatasetList key={refreshKey} onSelectDataset={handleSelectDataset} />
                </div>
              )}
            </div>

            {/* Quick Actions */}
            <div className="mt-6 grid md:grid-cols-2 gap-4">
              <Link
                href="/projects/new"
                className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 border border-gray-200 dark:border-gray-700 hover:shadow-xl transition-shadow"
              >
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                  Create New Project
                </h3>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Start a new time series analysis project
                </p>
              </Link>

              <Link
                href="/projects"
                className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 border border-gray-200 dark:border-gray-700 hover:shadow-xl transition-shadow"
              >
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                  View All Projects
                </h3>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Manage your existing projects
                </p>
              </Link>
            </div>

            {/* Quick Start Guide */}
            <div className="mt-6 bg-white dark:bg-gray-800 rounded-lg shadow-lg p-8 border border-gray-200 dark:border-gray-700">
              <h2 className="text-xl font-semibold mb-4 text-gray-900 dark:text-white">
                Quick Start Guide
              </h2>
              <ol className="space-y-3 text-gray-700 dark:text-gray-300">
                <li className="flex gap-3">
                  <span className="font-bold text-green-600 dark:text-green-400">1.</span>
                  <span>Upload your time series data file (CSV, Excel, or TXT)</span>
                </li>
                <li className="flex gap-3">
                  <span className="font-bold text-green-600 dark:text-green-400">2.</span>
                  <span>Select your dataset and configure date and target columns</span>
                </li>
                <li className="flex gap-3">
                  <span className="font-bold text-green-600 dark:text-green-400">3.</span>
                  <span>Test stationarity and transform your data if needed</span>
                </li>
                <li className="flex gap-3">
                  <span className="font-bold text-green-600 dark:text-green-400">4.</span>
                  <span>Train a SARIMAX model with automatic parameter estimation</span>
                </li>
                <li className="flex gap-3">
                  <span className="font-bold text-green-600 dark:text-green-400">5.</span>
                  <span>Generate forecasts and export your analysis code</span>
                </li>
              </ol>
            </div>
          </div>
        </div>
      </div>
    </ErrorBoundary>
  );
}
