"use client";

import React from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
} from "recharts";

interface ACFPACFChartProps {
  acf: number[];
  pacf: number[];
  lags: number[];
  confidenceInterval: { lower: number; upper: number };
}

export function ACFPACFChart({
  acf,
  pacf,
  lags,
  confidenceInterval,
}: ACFPACFChartProps) {
  const acfData = lags.map((lag, idx) => ({
    lag,
    acf: acf[idx],
    pacf: pacf[idx],
  }));

  return (
    <div className="w-full space-y-8">
      <div className="h-64">
        <h3 className="text-lg font-semibold mb-4">ACF (Autocorrelation Function)</h3>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={acfData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="lag" />
            <YAxis />
            <Tooltip />
            <ReferenceLine y={confidenceInterval.upper} stroke="#ef4444" strokeDasharray="3 3" />
            <ReferenceLine y={confidenceInterval.lower} stroke="#ef4444" strokeDasharray="3 3" />
            <ReferenceLine y={0} stroke="#000" />
            <Bar dataKey="acf" fill="#22c55e" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="h-64">
        <h3 className="text-lg font-semibold mb-4">PACF (Partial Autocorrelation Function)</h3>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={acfData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="lag" />
            <YAxis />
            <Tooltip />
            <ReferenceLine y={confidenceInterval.upper} stroke="#ef4444" strokeDasharray="3 3" />
            <ReferenceLine y={confidenceInterval.lower} stroke="#ef4444" strokeDasharray="3 3" />
            <ReferenceLine y={0} stroke="#000" />
            <Bar dataKey="pacf" fill="#3b82f6" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

