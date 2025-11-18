"use client";

import React, { useState, useMemo, useEffect, useRef } from "react";
import {
  ComposedChart,
  Line,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Brush,
  ReferenceLine,
} from "recharts";

interface ForecastChartProps {
  historical?: Array<{ date: string; value: number }>;
  forecasts: Array<{ date: string; value: number }>;
  confidenceIntervals: Array<{ date: string; lower: number; upper: number }>;
  title?: string;
}

export function ForecastChart({
  historical = [],
  forecasts,
  confidenceIntervals,
  title = "Forecast Visualization",
}: ForecastChartProps) {
  // Memoize data preparation to prevent unnecessary recalculations
  // Ensure continuity: forecast starts from the last historical point
  const forecastData = useMemo(() => {
    const lastHistoricalValue = historical.length > 0 ? historical[historical.length - 1].value : null;
    
    return forecasts.map((item, idx) => ({
      date: item.date,
      forecast: item.value,
      lower: confidenceIntervals[idx]?.lower ?? item.value,
      upper: confidenceIntervals[idx]?.upper ?? item.value,
      historical: null, // No historical data for forecast period
      // For continuity, we'll add a bridge point if this is the first forecast
      isFirstForecast: idx === 0,
      lastHistoricalValue: idx === 0 ? lastHistoricalValue : null,
    }));
  }, [forecasts, confidenceIntervals, historical]);

  // Prepare historical data
  const historicalData = useMemo(() => {
    return historical.map((item, idx) => ({
      date: item.date,
      historical: item.value,
      forecast: null,
      lower: null,
      upper: null,
      isLastHistorical: idx === historical.length - 1,
    }));
  }, [historical]);

  // Combine data - historical first, then forecasts
  // Add a bridge point to ensure continuity: duplicate the last historical point
  // as the first forecast point so lines connect smoothly
  const allData = useMemo(() => {
    if (historicalData.length === 0) {
      return forecastData;
    }
    
    const lastHistorical = historicalData[historicalData.length - 1];
    const firstForecast = forecastData[0];
    
    // Create a bridge point: all lines converge at the last historical point
    // This is the beginning of the forecast, so all values (historical, forecast, CI) must meet here
    const lastHistoricalValue = lastHistorical.historical;
    const bridgePoint = {
      date: lastHistorical.date,
      historical: lastHistoricalValue, // Historical line ends here
      forecast: lastHistoricalValue, // Forecast line starts here (continuity)
      lower: lastHistoricalValue, // Lower CI converges here (beginning of forecast)
      upper: lastHistoricalValue, // Upper CI converges here (beginning of forecast)
      isBridge: true,
    };
    
    // Combine: historical data + bridge point + rest of forecasts
    return [...historicalData, bridgePoint, ...forecastData.slice(1)];
  }, [historicalData, forecastData]);
  
  // Ensure we have data to display
  if (allData.length === 0) {
    return (
      <div className="w-full p-8 text-center text-gray-500">
        No data available for visualization
      </div>
    );
  }

  // Calculate Y-axis domain based on actual data range
  const allValues: number[] = [];
  allData.forEach((item) => {
    if (item.historical !== null && item.historical !== undefined) {
      allValues.push(item.historical);
    }
    if (item.forecast !== null && item.forecast !== undefined) {
      allValues.push(item.forecast);
    }
    if (item.lower !== null && item.lower !== undefined) {
      allValues.push(item.lower);
    }
    if (item.upper !== null && item.upper !== undefined) {
      allValues.push(item.upper);
    }
  });

  const minValue = Math.min(...allValues);
  const maxValue = Math.max(...allValues);
  const range = maxValue - minValue;
  const padding = range * 0.1; // 10% padding on each side
  const yAxisDomain = [Math.max(0, minValue - padding), maxValue + padding];

  // Debug: log data to console
  console.log("ForecastChart data:", {
    historicalCount: historical.length,
    forecastCount: forecasts.length,
    sampleForecast: forecastData.slice(0, 3),
    sampleHistorical: historicalData.slice(-3),
    lastHistorical: historicalData[historicalData.length - 1],
    firstForecast: forecastData[0],
    yAxisDomain,
    minValue,
    maxValue,
    allDataLength: allData.length,
  });
  
  // Check if forecast values are all the same (flat line)
  const uniqueForecastValues = new Set(forecastData.map(d => d.forecast));
  if (uniqueForecastValues.size === 1) {
    console.warn("WARNING: All forecast values are the same!", forecastData[0]?.forecast);
  }
  
  // Check if historical data is present
  if (historical.length === 0) {
    console.warn("WARNING: No historical data available for visualization");
  }

  // Calculate data range for brush (allow zooming)
  const dataLength = useMemo(() => allData.length, [allData.length]);
  const defaultStartIndex = useMemo(() => Math.max(0, dataLength - Math.min(150, dataLength)), [dataLength]);
  const defaultEndIndex = useMemo(() => dataLength - 1, [dataLength]);
  
  // Brush state - updates immediately, completely independent of chart
  // Use lazy initialization to prevent recalculation
  const [brushStartIndex, setBrushStartIndex] = useState(() => {
    const len = allData.length;
    return Math.max(0, len - Math.min(150, len));
  });
  const [brushEndIndex, setBrushEndIndex] = useState(() => allData.length - 1);
  
  // Displayed range state - updates asynchronously, does not affect brush
  const [displayedStartIndex, setDisplayedStartIndex] = useState(() => {
    const len = allData.length;
    return Math.max(0, len - Math.min(150, len));
  });
  const [displayedEndIndex, setDisplayedEndIndex] = useState(() => allData.length - 1);
  
  // Use ref to track debounce timer
  const debounceTimerRef = useRef<NodeJS.Timeout | null>(null);
  
  // Update displayed range asynchronously when brush changes (debounced)
  // This runs independently and does NOT affect the brush state
  // Brush can move freely while chart updates happen in background
  useEffect(() => {
    // Only update if brush actually changed
    if (brushStartIndex === displayedStartIndex && brushEndIndex === displayedEndIndex) {
      return; // No change needed
    }
    
    // Clear any pending updates
    if (debounceTimerRef.current) {
      clearTimeout(debounceTimerRef.current);
    }
    
    // Debounce the chart update - brush can continue moving freely
    debounceTimerRef.current = setTimeout(() => {
      setDisplayedStartIndex(brushStartIndex);
      setDisplayedEndIndex(brushEndIndex);
    }, 200); // 200ms debounce - chart updates after user stops dragging
    
    return () => {
      if (debounceTimerRef.current) {
        clearTimeout(debounceTimerRef.current);
      }
    };
  }, [brushStartIndex, brushEndIndex, displayedStartIndex, displayedEndIndex]);
  
  // Memoize displayed data to avoid recalculation on every render
  const displayedData = useMemo(() => {
    return allData.slice(displayedStartIndex, displayedEndIndex + 1);
  }, [allData, displayedStartIndex, displayedEndIndex]);
  
  // Memoize Y-axis domain calculation
  const displayedYAxisDomain = useMemo(() => {
    const displayedValues: number[] = [];
    displayedData.forEach((item) => {
      if (item.historical !== null && item.historical !== undefined) {
        displayedValues.push(item.historical);
      }
      if (item.forecast !== null && item.forecast !== undefined) {
        displayedValues.push(item.forecast);
      }
      if (item.lower !== null && item.lower !== undefined) {
        displayedValues.push(item.lower);
      }
      if (item.upper !== null && item.upper !== undefined) {
        displayedValues.push(item.upper);
      }
    });
    
    if (displayedValues.length === 0) {
      return yAxisDomain;
    }
    
    const displayedMinValue = Math.min(...displayedValues);
    const displayedMaxValue = Math.max(...displayedValues);
    const displayedRange = displayedMaxValue - displayedMinValue;
    const displayedPadding = displayedRange * 0.1;
    return [Math.max(0, displayedMinValue - displayedPadding), displayedMaxValue + displayedPadding];
  }, [displayedData, yAxisDomain]);

  return (
    <div className="w-full">
      {title && <h3 className="text-lg font-semibold mb-4">{title}</h3>}
      <div className="h-96">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={displayedData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis
              dataKey="date"
              angle={-45}
              textAnchor="end"
              height={80}
              tick={{ fontSize: 12 }}
              stroke="#6b7280"
              interval="preserveStartEnd"
            />
            <YAxis 
              domain={displayedYAxisDomain}
              stroke="#6b7280"
              allowDataOverflow={false}
            />
            <Tooltip
              formatter={(value: any, name: string) => {
                if (value === null || value === undefined) return null;
                return [typeof value === 'number' ? value.toFixed(2) : value, name];
              }}
              contentStyle={{
                backgroundColor: 'rgba(255, 255, 255, 0.95)',
                border: '1px solid #e5e7eb',
                borderRadius: '4px',
              }}
            />
            <Legend 
              wrapperStyle={{ paddingTop: '20px' }}
            />
                    {/* Reference line to show transition from historical to forecast */}
                    {historical.length > 0 && displayedEndIndex >= historical.length - 1 && (
                      <ReferenceLine 
                        x={historicalData[historicalData.length - 1]?.date} 
                        stroke="#ef4444" 
                        strokeDasharray="2 2"
                        strokeWidth={1}
                        label={{ value: "Forecast Start", position: "top", fill: "#ef4444", fontSize: 10 }}
                      />
                    )}
                    {/* Confidence interval area - filled between upper and lower */}
                    <Area
                      type="monotone"
                      dataKey="upper"
                      stroke="none"
                      fill="#fbbf24"
                      fillOpacity={0.15}
                      connectNulls={true}
                      name=""
                    />
                    <Area
                      type="monotone"
                      dataKey="lower"
                      stroke="none"
                      fill="#ffffff"
                      fillOpacity={1}
                      connectNulls={true}
                      name=""
                    />
                    {/* Historical line - Blue solid - connects to forecast for continuity */}
                    {historical.length > 0 && (
                      <Line
                        type="monotone"
                        dataKey="historical"
                        stroke="#3b82f6"
                        strokeWidth={2.5}
                        dot={false}
                        name={`Historical (${historical.length} points)`}
                        connectNulls={true}
                        activeDot={{ r: 4 }}
                      />
                    )}
                    {/* Upper CI line - Orange dashed - connects for continuity */}
                    <Line
                      type="monotone"
                      dataKey="upper"
                      stroke="#f97316"
                      strokeWidth={1.5}
                      strokeDasharray="4 4"
                      dot={false}
                      name="Upper CI (95%)"
                      connectNulls={true}
                    />
                    {/* Forecast line - Green dashed with dots - connects from historical */}
                    <Line
                      type="monotone"
                      dataKey="forecast"
                      stroke="#22c55e"
                      strokeWidth={3}
                      strokeDasharray="6 4"
                      dot={true}
                      dotSize={5}
                      dotFill="#22c55e"
                      name="Forecast"
                      connectNulls={true}
                    />
                    {/* Lower CI line - Orange dashed - connects for continuity */}
                    <Line
                      type="monotone"
                      dataKey="lower"
                      stroke="#f97316"
                      strokeWidth={1.5}
                      strokeDasharray="4 4"
                      dot={false}
                      name="Lower CI (95%)"
                      connectNulls={true}
                    />
          </ComposedChart>
        </ResponsiveContainer>
      </div>
      
      {/* Brush component for zooming/panning - completely independent */}
      <div className="h-20">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={allData}>
            <XAxis
              dataKey="date"
              tick={false}
              axisLine={false}
              height={1}
            />
            <YAxis
              domain={yAxisDomain}
              tick={false}
              axisLine={false}
              width={1}
            />
            <Brush
              dataKey="date"
              height={30}
              stroke="#3b82f6"
              fill="#e0e7ff"
              startIndex={brushStartIndex}
              endIndex={brushEndIndex}
              onChange={(brushData: any) => {
                // CRITICAL: Update brush state IMMEDIATELY with no delays
                // The brush must be completely independent and responsive
                // Chart updates happen separately via useEffect debounce
                if (brushData && typeof brushData.startIndex === 'number' && typeof brushData.endIndex === 'number') {
                  // Direct synchronous state update - brush responds instantly
                  // Chart will catch up asynchronously without affecting brush
                  setBrushStartIndex(brushData.startIndex);
                  setBrushEndIndex(brushData.endIndex);
                }
              }}
              // Prevent brush from being controlled by external updates
              alwaysShowText={false}
              // Ensure brush is uncontrolled by chart state
              controlled={false}
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>
      
      {/* Zoom controls */}
      <div className="flex items-center justify-between mt-2 text-sm text-gray-600">
        <div className="flex gap-2">
          <button
            onClick={() => {
              const newStart = Math.max(0, brushStartIndex - 20);
              const newEnd = Math.min(dataLength - 1, brushEndIndex - 20);
              setBrushStartIndex(newStart);
              setBrushEndIndex(newEnd);
            }}
            className="px-3 py-1 bg-blue-50 hover:bg-blue-100 rounded border border-blue-200 text-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            disabled={brushStartIndex === 0}
          >
            ← Pan Left
          </button>
          <button
            onClick={() => {
              const newStart = Math.max(0, brushStartIndex + 20);
              const newEnd = Math.min(dataLength - 1, brushEndIndex + 20);
              setBrushStartIndex(newStart);
              setBrushEndIndex(newEnd);
            }}
            className="px-3 py-1 bg-blue-50 hover:bg-blue-100 rounded border border-blue-200 text-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            disabled={brushEndIndex === dataLength - 1}
          >
            Pan Right →
          </button>
          <button
            onClick={() => {
              const range = brushEndIndex - brushStartIndex;
              const center = Math.floor((brushStartIndex + brushEndIndex) / 2);
              const newRange = Math.max(10, Math.floor(range * 0.7)); // Zoom in by 30%
              const newStart = Math.max(0, center - Math.floor(newRange / 2));
              const newEnd = Math.min(dataLength - 1, newStart + newRange);
              setBrushStartIndex(newStart);
              setBrushEndIndex(newEnd);
            }}
            className="px-3 py-1 bg-green-50 hover:bg-green-100 rounded border border-green-200 text-green-700"
          >
            Zoom In
          </button>
          <button
            onClick={() => {
              const range = brushEndIndex - brushStartIndex;
              const center = Math.floor((brushStartIndex + brushEndIndex) / 2);
              const newRange = Math.min(dataLength, Math.floor(range * 1.5)); // Zoom out by 50%
              const newStart = Math.max(0, center - Math.floor(newRange / 2));
              const newEnd = Math.min(dataLength - 1, newStart + newRange);
              setBrushStartIndex(newStart);
              setBrushEndIndex(newEnd);
            }}
            className="px-3 py-1 bg-green-50 hover:bg-green-100 rounded border border-green-200 text-green-700"
          >
            Zoom Out
          </button>
          <button
            onClick={() => {
              setBrushStartIndex(defaultStartIndex);
              setBrushEndIndex(defaultEndIndex);
            }}
            className="px-3 py-1 bg-gray-50 hover:bg-gray-100 rounded border border-gray-200 text-gray-700"
          >
            Reset View
          </button>
        </div>
        <div className="text-xs text-gray-500">
          Showing {displayedEndIndex - displayedStartIndex + 1} of {dataLength} data points
        </div>
      </div>
    </div>
  );
}
