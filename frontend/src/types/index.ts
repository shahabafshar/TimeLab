/**
 * Shared TypeScript types
 */

export interface Dataset {
  id: string;
  name: string;
  filename: string;
  columns: string[];
  row_count: number;
  created_at: string;
  updated_at?: string;
}

export interface TimeSeries {
  id: string;
  datasetId: string;
  dateColumn: string;
  targetColumn: string;
  frequency: "Hourly" | "Daily" | "Monthly" | "Quarterly" | "Yearly";
  data: Array<{ date: string; value: number }>;
}

export interface Transformation {
  type: string;
  parameters?: Record<string, unknown>;
}

export interface StationarityResult {
  isStationary: boolean;
  testStatistic: number;
  pValue: number;
  criticalValues: Record<string, number>;
  transformation: Transformation;
  d: number;
  D: number;
}

export interface ACFPACFResult {
  acf: number[];
  pacf: number[];
  lags: number[];
  suggestedP: number;
  suggestedQ: number;
  suggestedP_seasonal: number;
  suggestedQ_seasonal: number;
}

export interface DecompositionResult {
  trend: Array<{ date: string; value: number }>;
  seasonal: Array<{ date: string; value: number }>;
  residual: Array<{ date: string; value: number }>;
}

export interface ModelParameters {
  p: number;
  d: number;
  q: number;
  P: number;
  D: number;
  Q: number;
  s: number;
}

export interface Model {
  id: string;
  name: string;
  type: string;
  parameters: ModelParameters;
  metrics?: ModelMetrics;
  createdAt: string;
}

export interface ModelMetrics {
  rmse: number;
  mae: number;
  mape: number;
  aic: number;
  bic: number;
  hqic: number;
}

export interface Forecast {
  id: string;
  modelId: string;
  periods: number;
  values: Array<{ date: string; value: number; lower: number; upper: number }>;
  createdAt: string;
}

export interface Project {
  id: string;
  name: string;
  description?: string;
  dataset_id?: string;
  model_id?: string;
  created_at: string;
  updated_at?: string;
}

