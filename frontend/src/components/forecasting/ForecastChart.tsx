"use client";

import React from "react";
import { ForecastChart as BaseForecastChart } from "../charts/ForecastChart";

interface ForecastChartProps {
  historical?: Array<{ date: string; value: number }>;
  forecasts: Array<{ date: string; value: number }>;
  confidenceIntervals: Array<{ date: string; lower: number; upper: number }>;
}

export function ForecastChart(props: ForecastChartProps) {
  return <BaseForecastChart {...props} />;
}
