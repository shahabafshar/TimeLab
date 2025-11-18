"use client";

import React from "react";

interface Metrics {
  rmse?: number;
  mae?: number;
  mape?: number;
  aic?: number;
  bic?: number;
  hqic?: number;
}

interface MetricsTableProps {
  metrics: Metrics;
  title?: string;
}

export function MetricsTable({ metrics, title }: MetricsTableProps) {
  const metricRows = [
    { label: "RMSE", value: metrics.rmse },
    { label: "MAE", value: metrics.mae },
    { label: "MAPE", value: metrics.mape, suffix: "%" },
    { label: "AIC", value: metrics.aic },
    { label: "BIC", value: metrics.bic },
    { label: "HQIC", value: metrics.hqic },
  ].filter((row) => row.value !== undefined);

  return (
    <div className="w-full">
      {title && <h3 className="text-lg font-semibold mb-4">{title}</h3>}
      <div className="border rounded-md overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-2 text-left">Metric</th>
              <th className="px-4 py-2 text-right">Value</th>
            </tr>
          </thead>
          <tbody>
            {metricRows.map((row) => (
              <tr key={row.label} className="border-t">
                <td className="px-4 py-2">{row.label}</td>
                <td className="px-4 py-2 text-right font-mono">
                  {row.value?.toFixed(3)}
                  {row.suffix}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

