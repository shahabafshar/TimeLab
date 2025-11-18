"use client";

import React, { useState, useEffect } from "react";
import { useParams, useSearchParams, useRouter } from "next/navigation";
import { apiClient } from "../../../../src/lib/api-client";
import { LoadingSpinner } from "../../../../src/components/ui/LoadingSpinner";
import { TimeSeriesChart } from "../../../../src/components/charts/TimeSeriesChart";
import { ForecastChart } from "../../../../src/components/charts/ForecastChart";

export default function AnalyzePage() {
  const params = useParams();
  const searchParams = useSearchParams();
  const router = useRouter();
  const projectId = params.id as string;

  const dateColumn = searchParams.get("dateColumn") || "";
  const targetColumn = searchParams.get("targetColumn") || "";
  const frequency = searchParams.get("frequency") || "Monthly";

  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [loadingProject, setLoadingProject] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [stationarityResult, setStationarityResult] = useState<any>(null);
  const [acfPacfResult, setAcfPacfResult] = useState<any>(null);
  const [trainedModel, setTrainedModel] = useState<any>(null);
  const [forecastResult, setForecastResult] = useState<any>(null);
  const [forecastPeriods, setForecastPeriods] = useState<number>(12);
  const [project, setProject] = useState<any>(null);
  const [dataset, setDataset] = useState<any>(null);
  const [historicalData, setHistoricalData] = useState<Array<{ date: string; value: number }>>([]);

  // Load project and dataset on mount
          useEffect(() => {
            const loadProject = async () => {
              setLoadingProject(true);
              try {
                const projectData = await apiClient.get(`/projects/${projectId}`);
                setProject(projectData);
                
                if (projectData.dataset_id) {
                  const datasetData = await apiClient.get(`/datasets/${projectData.dataset_id}`);
                  setDataset(datasetData);
                  
                  // Load historical data for visualization
                  if (dateColumn && targetColumn) {
                    try {
                      const dataResponse = await apiClient.get(`/datasets/${projectData.dataset_id}/data`);
                      if (dataResponse && dataResponse.content) {
                        const csvData = dataResponse.content;
                        // Better CSV parsing - handle quoted values
                        const parseCSVLine = (line: string): string[] => {
                          const result: string[] = [];
                          let current = '';
                          let inQuotes = false;
                          
                          for (let i = 0; i < line.length; i++) {
                            const char = line[i];
                            if (char === '"') {
                              inQuotes = !inQuotes;
                            } else if (char === ',' && !inQuotes) {
                              result.push(current.trim());
                              current = '';
                            } else {
                              current += char;
                            }
                          }
                          result.push(current.trim());
                          return result;
                        };
                        
                        const lines = csvData.split('\n').filter(line => line.trim());
                        if (lines.length > 1) {
                          const headers = parseCSVLine(lines[0]);
                          const dateIdx = headers.indexOf(dateColumn);
                          const valueIdx = headers.indexOf(targetColumn);
                          
                          console.log("Loading historical data:", {
                            dateColumn,
                            targetColumn,
                            dateIdx,
                            valueIdx,
                            headers,
                            totalLines: lines.length
                          });
                          
                          if (dateIdx >= 0 && valueIdx >= 0) {
                            const histData = [];
                            for (let i = 1; i < lines.length; i++) {
                              const cols = parseCSVLine(lines[i]);
                              if (cols[dateIdx] && cols[valueIdx]) {
                                const value = parseFloat(cols[valueIdx]);
                                if (!isNaN(value)) {
                                  // Normalize date format
                                  let dateStr = cols[dateIdx].replace(/"/g, '');
                                  histData.push({
                                    date: dateStr,
                                    value: value,
                                  });
                                }
                              }
                            }
                            // Take last 100 points for better context, or all if less than 100
                            const finalData = histData.length > 100 ? histData.slice(-100) : histData;
                            console.log(`Loaded ${finalData.length} historical data points`, finalData.slice(0, 3));
                            setHistoricalData(finalData);
                          } else {
                            console.warn("Could not find columns in dataset:", { dateColumn, targetColumn, headers });
                          }
                        }
                      }
                    } catch (err) {
                      console.error("Could not load historical data:", err);
                    }
                  }
                }
              } catch (err) {
                setError(err instanceof Error ? err.message : "Failed to load project");
              } finally {
                setLoadingProject(false);
              }
            };
            
            if (projectId) {
              loadProject();
            }
          }, [projectId, dateColumn, targetColumn]);

  const handleTestStationarity = async () => {
    if (!project?.dataset_id || !dateColumn || !targetColumn) {
      setError("Missing required information: dataset, date column, or target column");
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const response = await apiClient.post("/preprocessing/test-stationarity", {
        dataset_id: project.dataset_id,
        date_column: dateColumn,
        target_column: targetColumn,
        frequency: frequency,
      });
      setStationarityResult(response);
      setStep(2);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to test stationarity");
    } finally {
      setLoading(false);
    }
  };

  const handleCalculateACFPACF = async () => {
    if (!project?.dataset_id || !dateColumn || !targetColumn) {
      setError("Missing required information: dataset, date column, or target column");
      return;
    }

    // Get seasonality from stationarity result or use default
    const seasonality = stationarityResult?.seasonality || 
      (frequency === "Monthly" ? 12 : frequency === "Quarterly" ? 4 : frequency === "Daily" ? 7 : 5);

    setLoading(true);
    setError(null);
    try {
      const response = await apiClient.post("/analysis/acf-pacf", {
        dataset_id: project.dataset_id,
        date_column: dateColumn,
        target_column: targetColumn,
        seasonality: seasonality,
      });
      setAcfPacfResult(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to calculate ACF/PACF");
    } finally {
      setLoading(false);
    }
  };

  const handleTrainModel = async () => {
    if (!project?.dataset_id || !dateColumn || !targetColumn || !acfPacfResult || !stationarityResult) {
      setError("Missing required information: dataset, date column, target column, or analysis results");
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const seasonality = stationarityResult.seasonality || 
        (frequency === "Monthly" ? 12 : frequency === "Quarterly" ? 4 : frequency === "Daily" ? 7 : 5);
      
      // Adjust parameters to avoid conflicts
      // q should be < seasonality to avoid overlap with seasonal MA component
      let q = acfPacfResult.suggested_parameters.q;
      if (q >= seasonality) {
        q = Math.max(0, seasonality - 1); // Cap q to avoid conflicts
      }
      
      // Ensure p is reasonable (typically < 5 for most time series)
      let p = Math.min(acfPacfResult.suggested_parameters.p, 5);
      
      const response = await apiClient.post("/models/train", {
        dataset_id: project.dataset_id,
        date_column: dateColumn,
        target_column: targetColumn,
        parameters: {
          p: p,
          d: stationarityResult.transformation?.d || 0,
          q: q,
          P: acfPacfResult.suggested_parameters.P,
          D: stationarityResult.transformation?.D || 0,
          Q: acfPacfResult.suggested_parameters.Q,
          s: seasonality,
        },
      });
      setTrainedModel(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to train model");
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateForecast = async () => {
    if (!trainedModel) {
      setError("No trained model available. Please train a model first.");
      return;
    }

    if (forecastPeriods < 1 || forecastPeriods > 120) {
      setError("Forecast periods must be between 1 and 120");
      return;
    }

    setLoading(true);
    setError(null);
    try {
      // Reload historical data if not already loaded
      if (historicalData.length === 0 && project?.dataset_id && dateColumn && targetColumn) {
        try {
          const dataResponse = await apiClient.get(`/datasets/${project.dataset_id}/data`);
          if (dataResponse && dataResponse.content) {
            const csvData = dataResponse.content;
            const parseCSVLine = (line: string): string[] => {
              const result: string[] = [];
              let current = '';
              let inQuotes = false;
              for (let i = 0; i < line.length; i++) {
                const char = line[i];
                if (char === '"') {
                  inQuotes = !inQuotes;
                } else if (char === ',' && !inQuotes) {
                  result.push(current.trim());
                  current = '';
                } else {
                  current += char;
                }
              }
              result.push(current.trim());
              return result;
            };
            const lines = csvData.split('\n').filter(line => line.trim());
            if (lines.length > 1) {
              const headers = parseCSVLine(lines[0]);
              const dateIdx = headers.indexOf(dateColumn);
              const valueIdx = headers.indexOf(targetColumn);
              if (dateIdx >= 0 && valueIdx >= 0) {
                const histData = [];
                for (let i = 1; i < lines.length; i++) {
                  const cols = parseCSVLine(lines[i]);
                  if (cols[dateIdx] && cols[valueIdx]) {
                    const value = parseFloat(cols[valueIdx]);
                    if (!isNaN(value)) {
                      histData.push({
                        date: cols[dateIdx].replace(/"/g, ''),
                        value: value,
                      });
                    }
                  }
                }
                const finalData = histData.length > 100 ? histData.slice(-100) : histData;
                setHistoricalData(finalData);
              }
            }
          }
        } catch (err) {
          console.warn("Could not reload historical data:", err);
        }
      }
      
      // Determine transformation type from stationarity result
      const transformationType = stationarityResult?.transformation?.type?.toLowerCase().includes("log") ? "log" : "none";
      
      const response = await apiClient.post(`/models/${trainedModel.id}/forecast`, {
        periods: forecastPeriods,
        transformation_type: transformationType,
      });
      setForecastResult(response);
    } catch (err: any) {
      // Better error handling - extract actual error message
      let errorMessage = "Failed to generate forecast";
      
      if (err instanceof Error) {
        errorMessage = err.message;
      } else if (typeof err === 'string') {
        errorMessage = err;
      } else if (err?.message) {
        errorMessage = typeof err.message === 'string' ? err.message : JSON.stringify(err.message);
      } else if (err?.response?.data?.detail) {
        errorMessage = typeof err.response.data.detail === 'string' 
          ? err.response.data.detail 
          : JSON.stringify(err.response.data.detail);
      } else if (err?.detail) {
        errorMessage = typeof err.detail === 'string' ? err.detail : JSON.stringify(err.detail);
      } else {
        // Last resort: stringify the whole error object
        try {
          errorMessage = JSON.stringify(err);
        } catch {
          errorMessage = "Failed to generate forecast (unknown error)";
        }
      }
      
      setError(errorMessage);
      console.error("Forecast error:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4 max-w-6xl">
        <div className="mb-6">
          <button
            onClick={() => router.back()}
            className="text-blue-600 hover:underline mb-4"
          >
            ← Back
          </button>
          <h1 className="text-3xl font-bold">Time Series Analysis</h1>
          <p className="text-gray-600 mt-2">
            Project ID: {projectId} • Date: {dateColumn} • Target: {targetColumn} • Frequency: {frequency}
          </p>
        </div>

        {/* Progress Steps */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <div className="flex justify-between items-center">
            {[1, 2, 3, 4, 5].map((s) => (
              <div key={s} className="flex items-center flex-1">
                <div
                  className={`w-10 h-10 rounded-full flex items-center justify-center ${
                    step >= s ? "bg-blue-600 text-white" : "bg-gray-200 text-gray-600"
                  }`}
                >
                  {s}
                </div>
                {s < 5 && (
                  <div
                    className={`flex-1 h-1 mx-2 ${
                      step > s ? "bg-blue-600" : "bg-gray-200"
                    }`}
                  />
                )}
              </div>
            ))}
          </div>
          <div className="flex justify-between mt-2 text-xs text-gray-500">
            <span>Transform</span>
            <span>Stationarity</span>
            <span>ACF/PACF</span>
            <span>Train Model</span>
            <span>Forecast</span>
          </div>
        </div>

        {/* Step Content */}
        <div className="bg-white rounded-lg shadow-sm p-6">
          {loadingProject ? (
            <div className="flex items-center justify-center py-12">
              <LoadingSpinner />
              <span className="ml-3 text-gray-600">Loading project data...</span>
            </div>
          ) : step === 1 ? (
            <div className="space-y-4">
              <h2 className="text-2xl font-semibold">Step 1: Test Stationarity</h2>
              <p className="text-gray-600">
                Test if your time series is stationary. If not, we'll help you transform it.
              </p>
              {project && dataset && (
                <div className="p-4 bg-blue-50 border border-blue-200 rounded-md mb-4">
                  <p className="text-sm text-blue-800">
                    <strong>Dataset:</strong> {dataset.name} ({dataset.row_count} rows)
                  </p>
                  <p className="text-sm text-blue-800 mt-1">
                    <strong>Date Column:</strong> {dateColumn} • <strong>Target Column:</strong> {targetColumn} • <strong>Frequency:</strong> {frequency}
                  </p>
                </div>
              )}
              <button
                onClick={handleTestStationarity}
                disabled={loading || !project?.dataset_id || !dateColumn || !targetColumn}
                className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? "Testing..." : "Test Stationarity"}
              </button>
              {(!project?.dataset_id || !dateColumn || !targetColumn) && (
                <p className="text-sm text-red-600 mt-2">
                  Please ensure all required fields are set: dataset, date column, and target column.
                </p>
              )}
            </div>
          ) : null}

          {step === 2 && stationarityResult && (
            <div className="space-y-4">
              <h2 className="text-2xl font-semibold">Stationarity Test Results</h2>
              <div className="p-4 bg-gray-50 rounded-md">
                <p className="font-medium">
                  Is Stationary: {stationarityResult.is_stationary ? "Yes ✓" : "No ✗"}
                </p>
                <p className="text-sm text-gray-600 mt-2">
                  Test Statistic: {stationarityResult.test_statistic.toFixed(4)}
                </p>
                <p className="text-sm text-gray-600">
                  P-value: {stationarityResult.p_value.toFixed(4)}
                </p>
                {stationarityResult.warnings.length > 0 && (
                  <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded">
                    {stationarityResult.warnings.map((w: string, i: number) => (
                      <p key={i} className="text-sm text-yellow-800">{w}</p>
                    ))}
                  </div>
                )}
              </div>
              <button
                onClick={() => {
                  setStep(3);
                  handleCalculateACFPACF();
                }}
                className="px-6 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
              >
                Continue to ACF/PACF Analysis
              </button>
            </div>
          )}

          {step === 3 && (
            <div className="space-y-4">
              {loading ? (
                <div className="flex items-center justify-center py-12">
                  <LoadingSpinner />
                  <span className="ml-3 text-gray-600">Calculating ACF/PACF...</span>
                </div>
              ) : acfPacfResult ? (
                <>
                  <h2 className="text-2xl font-semibold">Step 3: ACF/PACF Analysis</h2>
                  <p className="text-gray-600">
                    Autocorrelation Function (ACF) and Partial Autocorrelation Function (PACF) help identify model parameters.
                  </p>
                  
                  <div className="p-4 bg-blue-50 border border-blue-200 rounded-md">
                    <h3 className="font-semibold text-blue-900 mb-3">Suggested Model Parameters</h3>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      <div>
                        <p className="text-sm text-blue-700">AR (p)</p>
                        <p className="text-2xl font-bold text-blue-900">{acfPacfResult.suggested_parameters.p}</p>
                      </div>
                      <div>
                        <p className="text-sm text-blue-700">MA (q)</p>
                        <p className="text-2xl font-bold text-blue-900">{acfPacfResult.suggested_parameters.q}</p>
                      </div>
                      <div>
                        <p className="text-sm text-blue-700">Seasonal AR (P)</p>
                        <p className="text-2xl font-bold text-blue-900">{acfPacfResult.suggested_parameters.P}</p>
                      </div>
                      <div>
                        <p className="text-sm text-blue-700">Seasonal MA (Q)</p>
                        <p className="text-2xl font-bold text-blue-900">{acfPacfResult.suggested_parameters.Q}</p>
                      </div>
                    </div>
                  </div>

                  <div className="p-4 bg-gray-50 rounded-md">
                    <h3 className="font-semibold mb-2">Confidence Interval</h3>
                    <p className="text-sm text-gray-600">
                      Lower: {acfPacfResult.confidence_interval.lower.toFixed(4)} • 
                      Upper: {acfPacfResult.confidence_interval.upper.toFixed(4)}
                    </p>
                    <p className="text-xs text-gray-500 mt-2">
                      Values outside this range are statistically significant.
                    </p>
                  </div>

                  <div className="mt-4">
                    <p className="text-sm text-gray-600 mb-2">
                      <strong>ACF Values:</strong> {acfPacfResult.acf.slice(0, 10).map((v: number) => v.toFixed(3)).join(", ")}...
                    </p>
                    <p className="text-sm text-gray-600">
                      <strong>PACF Values:</strong> {acfPacfResult.pacf.slice(0, 10).map((v: number) => v.toFixed(3)).join(", ")}...
                    </p>
                  </div>

                  <button
                    onClick={() => {
                      setStep(4);
                      handleTrainModel();
                    }}
                    className="px-6 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
                  >
                    Continue to Model Training
                  </button>
                </>
              ) : (
                <div className="space-y-4">
                  <h2 className="text-2xl font-semibold">Step 3: ACF/PACF Analysis</h2>
                  <p className="text-gray-600">
                    Click the button below to calculate ACF and PACF values.
                  </p>
                  <button
                    onClick={handleCalculateACFPACF}
                    disabled={loading || !project?.dataset_id || !dateColumn || !targetColumn}
                    className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {loading ? "Calculating..." : "Calculate ACF/PACF"}
                  </button>
                </div>
              )}
            </div>
          )}

          {step === 4 && (
            <div className="space-y-4">
              {loading ? (
                <div className="flex items-center justify-center py-12">
                  <LoadingSpinner />
                  <span className="ml-3 text-gray-600">Training model... This may take a moment.</span>
                </div>
              ) : trainedModel ? (
                <>
                  <h2 className="text-2xl font-semibold">Step 4: Model Training Complete</h2>
                  <p className="text-gray-600">
                    Your SARIMAX model has been successfully trained.
                  </p>
                  
                  <div className="p-4 bg-green-50 border border-green-200 rounded-md">
                    <h3 className="font-semibold text-green-900 mb-3">Model Information</h3>
                    <p className="text-sm text-green-800 mb-2">
                      <strong>Model Name:</strong> {trainedModel.name}
                    </p>
                    <p className="text-sm text-green-800 mb-2">
                      <strong>Type:</strong> {trainedModel.type}
                    </p>
                    <div className="mt-3">
                      <p className="text-sm font-semibold text-green-900 mb-2">Parameters:</p>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-xs">
                        <div>
                          <span className="text-green-700">p:</span> {trainedModel.parameters.p}
                        </div>
                        <div>
                          <span className="text-green-700">d:</span> {trainedModel.parameters.d}
                        </div>
                        <div>
                          <span className="text-green-700">q:</span> {trainedModel.parameters.q}
                        </div>
                        <div>
                          <span className="text-green-700">P:</span> {trainedModel.parameters.P}
                        </div>
                        <div>
                          <span className="text-green-700">D:</span> {trainedModel.parameters.D}
                        </div>
                        <div>
                          <span className="text-green-700">Q:</span> {trainedModel.parameters.Q}
                        </div>
                        <div>
                          <span className="text-green-700">s:</span> {trainedModel.parameters.s}
                        </div>
                      </div>
                    </div>
                  </div>

                  {trainedModel.metrics && (
                    <div className="p-4 bg-blue-50 border border-blue-200 rounded-md">
                      <h3 className="font-semibold text-blue-900 mb-3">Model Metrics</h3>
                      <div className="grid grid-cols-3 gap-4">
                        <div>
                          <p className="text-sm text-blue-700">AIC</p>
                          <p className="text-xl font-bold text-blue-900">{trainedModel.metrics.aic?.toFixed(2) || 'N/A'}</p>
                        </div>
                        <div>
                          <p className="text-sm text-blue-700">BIC</p>
                          <p className="text-xl font-bold text-blue-900">{trainedModel.metrics.bic?.toFixed(2) || 'N/A'}</p>
                        </div>
                        <div>
                          <p className="text-sm text-blue-700">HQIC</p>
                          <p className="text-xl font-bold text-blue-900">{trainedModel.metrics.hqic?.toFixed(2) || 'N/A'}</p>
                        </div>
                      </div>
                      <p className="text-xs text-blue-600 mt-3">
                        Lower values indicate better model fit.
                      </p>
                    </div>
                  )}

                  <button
                    onClick={() => {
                      setStep(5);
                      handleGenerateForecast();
                    }}
                    className="px-6 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
                  >
                    Continue to Forecasting
                  </button>
                </>
              ) : (
                <div className="space-y-4">
                  <h2 className="text-2xl font-semibold">Step 4: Train Model</h2>
                  <p className="text-gray-600">
                    Train a SARIMAX model using the parameters suggested from ACF/PACF analysis.
                  </p>
                  {acfPacfResult && (
                    <div className="p-4 bg-blue-50 border border-blue-200 rounded-md mb-4">
                      <p className="text-sm text-blue-800 mb-2">
                        <strong>Suggested Parameters:</strong> p={acfPacfResult.suggested_parameters.p}, 
                        q={acfPacfResult.suggested_parameters.q}, 
                        P={acfPacfResult.suggested_parameters.P}, 
                        Q={acfPacfResult.suggested_parameters.Q}
                      </p>
                      <p className="text-xs text-blue-600">
                        Using d={stationarityResult?.transformation?.d || 0}, 
                        D={stationarityResult?.transformation?.D || 0}, 
                        s={stationarityResult?.seasonality || 12}
                      </p>
                    </div>
                  )}
                  <button
                    onClick={handleTrainModel}
                    disabled={loading || !project?.dataset_id || !dateColumn || !targetColumn || !acfPacfResult}
                    className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {loading ? "Training..." : "Train Model"}
                  </button>
                </div>
              )}
            </div>
          )}

          {step === 5 && (
            <div className="space-y-4">
              {loading ? (
                <div className="flex items-center justify-center py-12">
                  <LoadingSpinner />
                  <span className="ml-3 text-gray-600">Generating forecast... This may take a moment.</span>
                </div>
              ) : forecastResult ? (
                <>
                  <h2 className="text-2xl font-semibold">Step 5: Forecast Results</h2>
                  <p className="text-gray-600">
                    Your time series forecast has been generated successfully.
                  </p>
                  
                  <div className="p-4 bg-green-50 border border-green-200 rounded-md">
                    <h3 className="font-semibold text-green-900 mb-3">Forecast Summary</h3>
                    <p className="text-sm text-green-800 mb-2">
                      <strong>Forecast Periods:</strong> {forecastPeriods}
                    </p>
                    <p className="text-sm text-green-800">
                      <strong>Forecast Dates:</strong> {forecastResult.forecasts.dates.length} periods
                    </p>
                  </div>

                  {/* Forecast Visualization */}
                  <div className="p-4 bg-white border border-gray-200 rounded-md">
                    <div className="mb-4 flex items-center justify-between">
                      <div>
                        <h3 className="text-lg font-semibold mb-1">Forecast Visualization</h3>
                        <p className="text-sm text-gray-600">
                          {historicalData.length > 0 
                            ? `Showing ${historicalData.length} historical data points and ${forecastResult.forecasts.dates.length} forecast periods`
                            : `Showing ${forecastResult.forecasts.dates.length} forecast periods`}
                        </p>
                      </div>
                    </div>
                    <ForecastChart
                      historical={historicalData}
                      forecasts={forecastResult.forecasts.dates.map((date: string, idx: number) => ({
                        date: date,
                        value: forecastResult.forecasts.values[idx],
                      }))}
                      confidenceIntervals={forecastResult.forecasts.dates.map((date: string, idx: number) => ({
                        date: date,
                        lower: forecastResult.confidence_intervals.lower[idx],
                        upper: forecastResult.confidence_intervals.upper[idx],
                      }))}
                      title=""
                    />
                  </div>

                  <div className="p-4 bg-blue-50 border border-blue-200 rounded-md">
                    <h3 className="font-semibold text-blue-900 mb-3">Forecast Values</h3>
                    <div className="max-h-60 overflow-y-auto">
                      <table className="w-full text-sm">
                        <thead>
                          <tr className="border-b">
                            <th className="text-left py-2 px-3 text-blue-700">Date</th>
                            <th className="text-right py-2 px-3 text-blue-700">Forecast</th>
                            <th className="text-right py-2 px-3 text-blue-700">Lower CI</th>
                            <th className="text-right py-2 px-3 text-blue-700">Upper CI</th>
                          </tr>
                        </thead>
                        <tbody>
                          {forecastResult.forecasts.dates.slice(0, 20).map((date: string, idx: number) => (
                            <tr key={idx} className="border-b">
                              <td className="py-2 px-3 text-blue-800">{new Date(date).toLocaleDateString()}</td>
                              <td className="text-right py-2 px-3 text-blue-900 font-medium">
                                {forecastResult.forecasts.values[idx]?.toFixed(2) || 'N/A'}
                              </td>
                              <td className="text-right py-2 px-3 text-blue-700">
                                {forecastResult.confidence_intervals.lower[idx]?.toFixed(2) || 'N/A'}
                              </td>
                              <td className="text-right py-2 px-3 text-blue-700">
                                {forecastResult.confidence_intervals.upper[idx]?.toFixed(2) || 'N/A'}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                      {forecastResult.forecasts.dates.length > 20 && (
                        <p className="text-xs text-blue-600 mt-2 text-center">
                          Showing first 20 of {forecastResult.forecasts.dates.length} forecasts
                        </p>
                      )}
                    </div>
                  </div>

                  <div className="p-4 bg-gray-50 rounded-md">
                    <h3 className="font-semibold mb-2">Forecast Statistics</h3>
                    <div className="grid grid-cols-3 gap-4 text-sm">
                      <div>
                        <p className="text-gray-600">Mean Forecast</p>
                        <p className="text-lg font-bold text-gray-900">
                          {(forecastResult.forecasts.values.reduce((a: number, b: number) => a + b, 0) / forecastResult.forecasts.values.length).toFixed(2)}
                        </p>
                      </div>
                      <div>
                        <p className="text-gray-600">Min Forecast</p>
                        <p className="text-lg font-bold text-gray-900">
                          {Math.min(...forecastResult.forecasts.values).toFixed(2)}
                        </p>
                      </div>
                      <div>
                        <p className="text-gray-600">Max Forecast</p>
                        <p className="text-lg font-bold text-gray-900">
                          {Math.max(...forecastResult.forecasts.values).toFixed(2)}
                        </p>
                      </div>
                    </div>
                  </div>

                  <div className="flex gap-4">
                    <button
                      onClick={() => {
                        setForecastResult(null);
                        setForecastPeriods(12);
                      }}
                      className="px-6 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700"
                    >
                      Generate New Forecast
                    </button>
                    <button
                      onClick={() => {
                        // TODO: Implement code export
                        alert("Code export feature coming soon!");
                      }}
                      className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                    >
                      Export Code
                    </button>
                  </div>
                </>
              ) : (
                <div className="space-y-4">
                  <h2 className="text-2xl font-semibold">Step 5: Generate Forecast</h2>
                  <p className="text-gray-600">
                    Generate future predictions using your trained model.
                  </p>
                  
                  <div className="p-4 bg-blue-50 border border-blue-200 rounded-md">
                    <label className="block text-sm font-medium text-blue-900 mb-2">
                      Number of Periods to Forecast
                    </label>
                    <input
                      type="number"
                      min="1"
                      max="120"
                      value={forecastPeriods}
                      onChange={(e) => setForecastPeriods(parseInt(e.target.value) || 12)}
                      className="w-full px-4 py-2 border border-blue-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                    <p className="text-xs text-blue-600 mt-2">
                      Recommended: {stationarityResult?.seasonality || 12} periods (1 season)
                    </p>
                  </div>

                  {trainedModel && (
                    <div className="p-4 bg-gray-50 rounded-md mb-4">
                      <p className="text-sm text-gray-700">
                        <strong>Model:</strong> {trainedModel.name}
                      </p>
                      <p className="text-xs text-gray-600 mt-1">
                        Transformation: {stationarityResult?.transformation?.type || "None"}
                      </p>
                    </div>
                  )}

                  <button
                    onClick={handleGenerateForecast}
                    disabled={loading || !trainedModel}
                    className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {loading ? "Generating..." : "Generate Forecast"}
                  </button>
                </div>
              )}
            </div>
          )}

          {error && (
            <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-md text-red-700">
              {error}
            </div>
          )}
        </div>

        {/* Quick Actions */}
        <div className="mt-6 bg-white rounded-lg shadow-sm p-6">
          <h3 className="font-semibold mb-4">Quick Actions</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <button className="p-4 border rounded-lg hover:bg-gray-50 text-left">
              <div className="font-medium">View Dataset</div>
              <div className="text-sm text-gray-500">See raw data</div>
            </button>
            <button className="p-4 border rounded-lg hover:bg-gray-50 text-left">
              <div className="font-medium">Decompose</div>
              <div className="text-sm text-gray-500">Trend & Seasonality</div>
            </button>
            <button className="p-4 border rounded-lg hover:bg-gray-50 text-left">
              <div className="font-medium">Train Model</div>
              <div className="text-sm text-gray-500">SARIMAX</div>
            </button>
            <button className="p-4 border rounded-lg hover:bg-gray-50 text-left">
              <div className="font-medium">Forecast</div>
              <div className="text-sm text-gray-500">Generate predictions</div>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

