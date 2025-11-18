"use client";

import React from "react";

interface ModelMetrics {
  rmse?: number;
  mae?: number;
  mape?: number;
  aic?: number;
  bic?: number;
  hqic?: number;
}

interface ModelSummaryProps {
  summary: string;
  metrics?: ModelMetrics;
}

export function ModelSummary({ summary, metrics }: ModelSummaryProps) {
  return (
    <div className="space-y-4">
      <div>
        <h3 className="text-lg font-semibold mb-2">Model Summary</h3>
        <pre className="bg-gray-100 p-4 rounded-md overflow-auto text-sm">
          {summary}
        </pre>
      </div>

      {metrics && (
        <div>
          <h3 className="text-lg font-semibold mb-2">Metrics</h3>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            {metrics.rmse && (
              <div className="p-4 border rounded-md">
                <div className="text-sm text-gray-600">RMSE</div>
                <div className="text-2xl font-bold">{metrics.rmse.toFixed(3)}</div>
              </div>
            )}
            {metrics.mae && (
              <div className="p-4 border rounded-md">
                <div className="text-sm text-gray-600">MAE</div>
                <div className="text-2xl font-bold">{metrics.mae.toFixed(3)}</div>
              </div>
            )}
            {metrics.mape && (
              <div className="p-4 border rounded-md">
                <div className="text-sm text-gray-600">MAPE</div>
                <div className="text-2xl font-bold">{metrics.mape.toFixed(2)}%</div>
              </div>
            )}
            {metrics.aic && (
              <div className="p-4 border rounded-md">
                <div className="text-sm text-gray-600">AIC</div>
                <div className="text-2xl font-bold">{metrics.aic.toFixed(2)}</div>
              </div>
            )}
            {metrics.bic && (
              <div className="p-4 border rounded-md">
                <div className="text-sm text-gray-600">BIC</div>
                <div className="text-2xl font-bold">{metrics.bic.toFixed(2)}</div>
              </div>
            )}
            {metrics.hqic && (
              <div className="p-4 border rounded-md">
                <div className="text-sm text-gray-600">HQIC</div>
                <div className="text-2xl font-bold">{metrics.hqic.toFixed(2)}</div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

