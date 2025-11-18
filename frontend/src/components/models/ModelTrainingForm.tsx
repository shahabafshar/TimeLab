"use client";

import React, { useState } from "react";

interface ModelParameters {
  p: number;
  d: number;
  q: number;
  P: number;
  D: number;
  Q: number;
  s: number;
}

interface ModelTrainingFormProps {
  suggestedParams?: ModelParameters;
  onSubmit: (params: ModelParameters) => void;
  onGridSearch?: () => void;
}

export function ModelTrainingForm({
  suggestedParams,
  onSubmit,
  onGridSearch,
}: ModelTrainingFormProps) {
  const [params, setParams] = useState<ModelParameters>(
    suggestedParams || {
      p: 1,
      d: 1,
      q: 1,
      P: 1,
      D: 1,
      Q: 1,
      s: 12,
    }
  );

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(params);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div>
          <label className="block text-sm font-medium mb-2">p (AR)</label>
          <input
            type="number"
            min="0"
            max="30"
            value={params.p}
            onChange={(e) => setParams({ ...params, p: parseInt(e.target.value) })}
            className="w-full px-3 py-2 border rounded-md"
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-2">d (I)</label>
          <input
            type="number"
            min="0"
            max="3"
            value={params.d}
            onChange={(e) => setParams({ ...params, d: parseInt(e.target.value) })}
            className="w-full px-3 py-2 border rounded-md"
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-2">q (MA)</label>
          <input
            type="number"
            min="0"
            max="30"
            value={params.q}
            onChange={(e) => setParams({ ...params, q: parseInt(e.target.value) })}
            className="w-full px-3 py-2 border rounded-md"
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-2">P (Seasonal AR)</label>
          <input
            type="number"
            min="0"
            max="30"
            value={params.P}
            onChange={(e) => setParams({ ...params, P: parseInt(e.target.value) })}
            className="w-full px-3 py-2 border rounded-md"
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-2">D (Seasonal I)</label>
          <input
            type="number"
            min="0"
            max="3"
            value={params.D}
            onChange={(e) => setParams({ ...params, D: parseInt(e.target.value) })}
            className="w-full px-3 py-2 border rounded-md"
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-2">Q (Seasonal MA)</label>
          <input
            type="number"
            min="0"
            max="30"
            value={params.Q}
            onChange={(e) => setParams({ ...params, Q: parseInt(e.target.value) })}
            className="w-full px-3 py-2 border rounded-md"
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-2">s (Seasonality)</label>
          <input
            type="number"
            min="0"
            max="30"
            value={params.s}
            onChange={(e) => setParams({ ...params, s: parseInt(e.target.value) })}
            className="w-full px-3 py-2 border rounded-md"
          />
        </div>
      </div>

      <div className="flex gap-4">
        <button
          type="submit"
          className="px-6 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
        >
          Train Model
        </button>
        {onGridSearch && (
          <button
            type="button"
            onClick={onGridSearch}
            className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            Grid Search
          </button>
        )}
      </div>
    </form>
  );
}

