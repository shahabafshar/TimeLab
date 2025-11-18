"use client";

import React from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

interface PredictionChartProps {
  actual: number[];
  predicted: number[];
  dates: string[];
  title?: string;
}

export function PredictionChart({
  actual,
  predicted,
  dates,
  title,
}: PredictionChartProps) {
  const data = dates.map((date, idx) => ({
    date,
    actual: actual[idx],
    predicted: predicted[idx],
  }));

  return (
    <div className="w-full h-96">
      {title && <h3 className="text-lg font-semibold mb-4">{title}</h3>}
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis
            dataKey="date"
            angle={-45}
            textAnchor="end"
            height={80}
          />
          <YAxis />
          <Tooltip />
          <Legend />
          <Line
            type="monotone"
            dataKey="actual"
            stroke="#22c55e"
            strokeWidth={2}
            name="Actual"
          />
          <Line
            type="monotone"
            dataKey="predicted"
            stroke="#ef4444"
            strokeWidth={2}
            name="Predicted"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

