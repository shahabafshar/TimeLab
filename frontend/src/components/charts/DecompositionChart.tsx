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

interface DecompositionChartProps {
  trend: Array<{ date: string; value: number }>;
  seasonal: Array<{ date: string; value: number }>;
  residual: Array<{ date: string; value: number }>;
}

export function DecompositionChart({
  trend,
  seasonal,
  residual,
}: DecompositionChartProps) {
  // Combine data for display
  const combinedData = trend.map((item, idx) => ({
    date: item.date,
    trend: item.value,
    seasonal: seasonal[idx]?.value || 0,
    residual: residual[idx]?.value || 0,
  }));

  return (
    <div className="w-full space-y-8">
      <div className="h-64">
        <h3 className="text-lg font-semibold mb-4">Trend</h3>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={trend}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" angle={-45} textAnchor="end" height={80} />
            <YAxis />
            <Tooltip />
            <Line type="monotone" dataKey="value" stroke="#22c55e" strokeWidth={2} />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="h-64">
        <h3 className="text-lg font-semibold mb-4">Seasonal</h3>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={seasonal}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" angle={-45} textAnchor="end" height={80} />
            <YAxis />
            <Tooltip />
            <Line type="monotone" dataKey="value" stroke="#3b82f6" strokeWidth={2} />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="h-64">
        <h3 className="text-lg font-semibold mb-4">Residual</h3>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={residual}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" angle={-45} textAnchor="end" height={80} />
            <YAxis />
            <Tooltip />
            <Line type="monotone" dataKey="value" stroke="#ef4444" strokeWidth={2} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

