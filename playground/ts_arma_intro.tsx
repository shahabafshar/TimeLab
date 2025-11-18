import React, { useState } from 'react';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ScatterChart, Scatter } from 'recharts';

export default function ARMAFundamentals() {
  const [selectedConcept, setSelectedConcept] = useState('what-is-ar');
  const [arCoeff, setArCoeff] = useState(0.7);
  const [maCoeff, setMaCoeff] = useState(0.5);
  const [noiseLevel, setNoiseLevel] = useState(2);

  // Generate AR(1): x(t) = φ*x(t-1) + noise
  const generateAR = (phi, n = 100) => {
    const series = [{ t: 1, value: 5 }];
    for (let i = 1; i < n; i++) {
      series.push({
        t: i + 1,
        value: phi * series[i - 1].value + (Math.random() - 0.5) * noiseLevel
      });
    }
    return series;
  };

  // Generate MA(1): x(t) = noise + θ*noise(t-1)
  const generateMA = (theta, n = 100) => {
    const noises = Array.from({ length: n + 1 }, () => (Math.random() - 0.5) * noiseLevel);
    const series = [];
    for (let i = 1; i < n; i++) {
      series.push({
        t: i,
        value: noises[i] + theta * noises[i - 1]
      });
    }
    return series;
  };

  // Generate pure noise for comparison
  const generateNoise = (n = 100) => {
    return Array.from({ length: n }, (_, i) => ({
      t: i + 1,
      value: (Math.random() - 0.5) * noiseLevel * 3
    }));
  };

  // Compute autocorrelation
  const computeACF = (data, maxLag = 15) => {
    const values = data.map(d => d.value);
    const n = values.length;
    const mean = values.reduce((a, b) => a + b) / n;
    const c0 = values.reduce((sum, x) => sum + Math.pow(x - mean, 2), 0) / n;
    
    const acf = [];
    for (let h = 0; h <= maxLag; h++) {
      let ch = 0;
      for (let t = 0; t < n - h; t++) {
        ch += (values[t] - mean) * (values[t + h] - mean);
      }
      acf.push({ lag: h, acf: ch / (n * c0) });
    }
    return acf;
  };

  const arSeries = generateAR(arCoeff);
  const arACF = computeACF(arSeries);
  const maSeries = generateMA(maCoeff);
  const maACF = computeACF(maSeries);
  const noiseSeries = generateNoise();
  const noiseACF = computeACF(noiseSeries);

  // Create lag plots (x(t) vs x(t+1))
  const createLagPlot = (data) => {
    const plot = [];
    for (let i = 0; i < data.length - 1; i++) {
      plot.push({
        current: data[i].value,
        next: data[i + 1].value
      });
    }
    return plot;
  };

  const arLagPlot = createLagPlot(arSeries);
  const maLagPlot = createLagPlot(maSeries);
  const noiseLagPlot = createLagPlot(noiseSeries);

  return (
    <div className="w-full h-screen bg-slate-900 overflow-auto">
      <div className="p-6 max-w-full">
        <h1 className="text-4xl font-bold text-white mb-2">Understanding ARMA: From the Ground Up</h1>
        <p className="text-slate-400 mb-8">What does each process actually do? See it visualized.</p>

        <div className="grid grid-cols-12 gap-6">
          {/* Left: Concept Navigator */}
          <div className="col-span-2">
            <div className="bg-slate-800 rounded-lg p-4 border border-slate-700 sticky top-6 space-y-3">
              <h2 className="text-white font-bold text-sm mb-4">Topics</h2>
              {[
                { id: 'what-is-ar', label: 'What is AR(1)?', emoji: '📊' },
                { id: 'what-is-ma', label: 'What is MA(1)?', emoji: '🌊' },
                { id: 'white-noise', label: 'White Noise', emoji: '⚪' },
                { id: 'ar-vs-ma', label: 'AR vs MA', emoji: '⚖️' },
              ].map(concept => (
                <button
                  key={concept.id}
                  onClick={() => setSelectedConcept(concept.id)}
                  className={`w-full text-left px-3 py-2 rounded text-sm transition-all ${
                    selectedConcept === concept.id
                      ? 'bg-blue-600 text-white'
                      : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                  }`}
                >
                  <div className="text-lg">{concept.emoji}</div>
                  <div className="font-semibold text-xs">{concept.label}</div>
                </button>
              ))}
            </div>
          </div>

          {/* Right: Main Content */}
          <div className="col-span-10">
            {selectedConcept === 'what-is-ar' && (
              <div className="space-y-6">
                <div className="bg-slate-800 rounded-lg p-6 border-2 border-blue-600">
                  <h2 className="text-blue-300 text-2xl font-bold mb-4">What is AR(1)?</h2>
                  
                  <div className="grid grid-cols-2 gap-6 mb-6">
                    <div>
                      <h3 className="text-slate-300 font-bold mb-3">The Idea</h3>
                      <div className="bg-slate-900 p-4 rounded text-slate-200 text-sm space-y-3">
                        <p><strong>AR = Autoregressive:</strong> depends on its own past</p>
                        <p>"Tomorrow's temp will be similar to today's, plus random variation"</p>
                        <div className="bg-slate-800 p-3 rounded font-mono text-blue-300">x(t) = φ × x(t-1) + ε(t)</div>
                      </div>
                    </div>

                    <div>
                      <h3 className="text-slate-300 font-bold mb-3">Real Examples</h3>
                      <div className="bg-slate-900 p-4 rounded text-xs text-slate-200 space-y-2">
                        <div className="border-l-4 border-blue-400 pl-2">
                          <strong>Stock Price:</strong> Today ≈ 0.8 × Yesterday + news
                        </div>
                        <div className="border-l-4 border-blue-400 pl-2">
                          <strong>Room Temp:</strong> Today ≈ 0.9 × Yesterday + AC
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="bg-slate-900 p-4 rounded mb-6">
                    <label className="text-slate-300 font-bold text-sm block mb-3">
                      Adjust φ: {arCoeff.toFixed(2)}
                    </label>
                    <input
                      type="range"
                      min="-0.95"
                      max="0.95"
                      step="0.05"
                      value={arCoeff}
                      onChange={(e) => setArCoeff(parseFloat(e.target.value))}
                      className="w-full h-2 bg-slate-600 rounded-lg appearance-none cursor-pointer"
                    />
                  </div>

                  <div className="grid grid-cols-3 gap-4">
                    <div className="bg-slate-800 rounded-lg p-4 border border-slate-700">
                      <h4 className="text-slate-300 font-bold text-xs mb-3">Time Series</h4>
                      <ResponsiveContainer width="100%" height={180}>
                        <LineChart data={arSeries} margin={{ top: 5, right: 10, left: -20, bottom: 15 }}>
                          <CartesianGrid strokeDasharray="3 3" stroke="#444" />
                          <XAxis dataKey="t" tick={{ fontSize: 9 }} />
                          <YAxis tick={{ fontSize: 9 }} />
                          <Line type="monotone" dataKey="value" stroke="#3b82f6" dot={false} strokeWidth={2} isAnimationActive={false} />
                        </LineChart>
                      </ResponsiveContainer>
                    </div>

                    <div className="bg-slate-800 rounded-lg p-4 border border-slate-700">
                      <h4 className="text-slate-300 font-bold text-xs mb-3">Lag Plot</h4>
                      <ResponsiveContainer width="100%" height={180}>
                        <ScatterChart margin={{ top: 5, right: 10, left: -20, bottom: 15 }}>
                          <CartesianGrid strokeDasharray="3 3" stroke="#444" />
                          <XAxis dataKey="current" type="number" tick={{ fontSize: 9 }} />
                          <YAxis dataKey="next" type="number" tick={{ fontSize: 9 }} />
                          <Scatter data={arLagPlot} fill="#3b82f6" opacity={0.5} />
                        </ScatterChart>
                      </ResponsiveContainer>
                    </div>

                    <div className="bg-slate-800 rounded-lg p-4 border border-slate-700">
                      <h4 className="text-slate-300 font-bold text-xs mb-3">ACF Pattern</h4>
                      <ResponsiveContainer width="100%" height={180}>
                        <BarChart data={arACF} margin={{ top: 5, right: 10, left: -20, bottom: 15 }}>
                          <CartesianGrid strokeDasharray="3 3" stroke="#444" />
                          <XAxis dataKey="lag" tick={{ fontSize: 9 }} />
                          <YAxis domain={[-0.5, 1]} tick={{ fontSize: 9 }} />
                          <Bar dataKey="acf" fill="#3b82f6" />
                        </BarChart>
                      </ResponsiveContainer>
                    </div>
                  </div>

                  <div className="bg-blue-900 p-4 rounded mt-6 border-l-4 border-blue-500">
                    <p className="text-sm text-slate-300">
                      <strong>AR Signature:</strong> ACF decays slowly with ρ(h) = φ^h. Strong persistence!
                    </p>
                  </div>
                </div>
              </div>
            )}

            {selectedConcept === 'what-is-ma' && (
              <div className="space-y-6">
                <div className="bg-slate-800 rounded-lg p-6 border-2 border-green-600">
                  <h2 className="text-green-300 text-2xl font-bold mb-4">What is MA(1)?</h2>
                  
                  <div className="grid grid-cols-2 gap-6 mb-6">
                    <div>
                      <h3 className="text-slate-300 font-bold mb-3">The Idea</h3>
                      <div className="bg-slate-900 p-4 rounded text-slate-200 text-sm space-y-3">
                        <p><strong>MA = Moving Average:</strong> depends on past shocks</p>
                        <p>"Today's demand = random spike + yesterday's leftover effect"</p>
                        <div className="bg-slate-800 p-3 rounded font-mono text-green-300">x(t) = ε(t) + θ × ε(t-1)</div>
                      </div>
                    </div>

                    <div>
                      <h3 className="text-slate-300 font-bold mb-3">Real Examples</h3>
                      <div className="bg-slate-900 p-4 rounded text-xs text-slate-200 space-y-2">
                        <div className="border-l-4 border-green-400 pl-2">
                          <strong>Measurement Error:</strong> Sensor noise + yesterday's glitch
                        </div>
                        <div className="border-l-4 border-green-400 pl-2">
                          <strong>Customer Demand:</strong> Random burst + delayed orders
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="bg-slate-900 p-4 rounded mb-6">
                    <label className="text-slate-300 font-bold text-sm block mb-3">
                      Adjust θ: {maCoeff.toFixed(2)}
                    </label>
                    <input
                      type="range"
                      min="-0.95"
                      max="0.95"
                      step="0.05"
                      value={maCoeff}
                      onChange={(e) => setMaCoeff(parseFloat(e.target.value))}
                      className="w-full h-2 bg-slate-600 rounded-lg appearance-none cursor-pointer"
                    />
                  </div>

                  <div className="grid grid-cols-3 gap-4">
                    <div className="bg-slate-800 rounded-lg p-4 border border-slate-700">
                      <h4 className="text-slate-300 font-bold text-xs mb-3">Time Series</h4>
                      <ResponsiveContainer width="100%" height={180}>
                        <LineChart data={maSeries} margin={{ top: 5, right: 10, left: -20, bottom: 15 }}>
                          <CartesianGrid strokeDasharray="3 3" stroke="#444" />
                          <XAxis dataKey="t" tick={{ fontSize: 9 }} />
                          <YAxis tick={{ fontSize: 9 }} />
                          <Line type="monotone" dataKey="value" stroke="#10b981" dot={false} strokeWidth={2} isAnimationActive={false} />
                        </LineChart>
                      </ResponsiveContainer>
                    </div>

                    <div className="bg-slate-800 rounded-lg p-4 border border-slate-700">
                      <h4 className="text-slate-300 font-bold text-xs mb-3">Lag Plot</h4>
                      <ResponsiveContainer width="100%" height={180}>
                        <ScatterChart margin={{ top: 5, right: 10, left: -20, bottom: 15 }}>
                          <CartesianGrid strokeDasharray="3 3" stroke="#444" />
                          <XAxis dataKey="current" type="number" tick={{ fontSize: 9 }} />
                          <YAxis dataKey="next" type="number" tick={{ fontSize: 9 }} />
                          <Scatter data={maLagPlot} fill="#10b981" opacity={0.5} />
                        </ScatterChart>
                      </ResponsiveContainer>
                    </div>

                    <div className="bg-slate-800 rounded-lg p-4 border border-slate-700">
                      <h4 className="text-slate-300 font-bold text-xs mb-3">ACF Pattern</h4>
                      <ResponsiveContainer width="100%" height={180}>
                        <BarChart data={maACF} margin={{ top: 5, right: 10, left: -20, bottom: 15 }}>
                          <CartesianGrid strokeDasharray="3 3" stroke="#444" />
                          <XAxis dataKey="lag" tick={{ fontSize: 9 }} />
                          <YAxis domain={[-0.5, 1]} tick={{ fontSize: 9 }} />
                          <Bar dataKey="acf" fill="#10b981" />
                        </BarChart>
                      </ResponsiveContainer>
                    </div>
                  </div>

                  <div className="bg-green-900 p-4 rounded mt-6 border-l-4 border-green-500">
                    <p className="text-sm text-slate-300">
                      <strong>MA Signature:</strong> ACF spikes at lag 1, then drops to zero. Sharp cutoff!
                    </p>
                  </div>
                </div>
              </div>
            )}

            {selectedConcept === 'white-noise' && (
              <div className="space-y-6">
                <div className="bg-slate-800 rounded-lg p-6 border-2 border-slate-500">
                  <h2 className="text-slate-300 text-2xl font-bold mb-4">White Noise: The Baseline</h2>
                  
                  <div className="grid grid-cols-2 gap-6 mb-6">
                    <div>
                      <h3 className="text-slate-300 font-bold mb-3">The Idea</h3>
                      <div className="bg-slate-900 p-4 rounded text-slate-200 text-sm space-y-3">
                        <p><strong>White Noise:</strong> Pure random. No patterns.</p>
                        <p>Each value is independent—no relationship to past</p>
                        <div className="bg-slate-800 p-3 rounded font-mono text-slate-300">x(t) = ε(t)</div>
                      </div>
                    </div>

                    <div>
                      <h3 className="text-slate-300 font-bold mb-3">Why It Matters</h3>
                      <div className="bg-slate-900 p-4 rounded text-xs text-slate-200 space-y-2">
                        <p>White noise is the NULL hypothesis. If your data is white noise:</p>
                        <ul className="list-disc list-inside text-slate-400">
                          <li>Can't forecast it</li>
                          <li>No patterns exist</li>
                          <li>Don't use ARMA</li>
                        </ul>
                      </div>
                    </div>
                  </div>

                  <div className="grid grid-cols-3 gap-4">
                    <div className="bg-slate-800 rounded-lg p-4 border border-slate-700">
                      <h4 className="text-slate-300 font-bold text-xs mb-3">Time Series</h4>
                      <ResponsiveContainer width="100%" height={180}>
                        <LineChart data={noiseSeries} margin={{ top: 5, right: 10, left: -20, bottom: 15 }}>
                          <CartesianGrid strokeDasharray="3 3" stroke="#444" />
                          <XAxis dataKey="t" tick={{ fontSize: 9 }} />
                          <YAxis tick={{ fontSize: 9 }} />
                          <Line type="monotone" dataKey="value" stroke="#888" dot={false} strokeWidth={2} isAnimationActive={false} />
                        </LineChart>
                      </ResponsiveContainer>
                    </div>

                    <div className="bg-slate-800 rounded-lg p-4 border border-slate-700">
                      <h4 className="text-slate-300 font-bold text-xs mb-3">Lag Plot</h4>
                      <ResponsiveContainer width="100%" height={180}>
                        <ScatterChart margin={{ top: 5, right: 10, left: -20, bottom: 15 }}>
                          <CartesianGrid strokeDasharray="3 3" stroke="#444" />
                          <XAxis dataKey="current" type="number" tick={{ fontSize: 9 }} />
                          <YAxis dataKey="next" type="number" tick={{ fontSize: 9 }} />
                          <Scatter data={noiseLagPlot} fill="#888" opacity={0.4} />
                        </ScatterChart>
                      </ResponsiveContainer>
                    </div>

                    <div className="bg-slate-800 rounded-lg p-4 border border-slate-700">
                      <h4 className="text-slate-300 font-bold text-xs mb-3">ACF Pattern</h4>
                      <ResponsiveContainer width="100%" height={180}>
                        <BarChart data={noiseACF} margin={{ top: 5, right: 10, left: -20, bottom: 15 }}>
                          <CartesianGrid strokeDasharray="3 3" stroke="#444" />
                          <XAxis dataKey="lag" tick={{ fontSize: 9 }} />
                          <YAxis domain={[-0.5, 1]} tick={{ fontSize: 9 }} />
                          <Bar dataKey="acf" fill="#888" />
                        </BarChart>
                      </ResponsiveContainer>
                    </div>
                  </div>

                  <div className="bg-slate-700 p-4 rounded mt-6 border-l-4 border-slate-500">
                    <p className="text-sm text-slate-300">
                      <strong>Baseline Signature:</strong> ACF all near zero. Nothing to model!
                    </p>
                  </div>
                </div>
              </div>
            )}

            {selectedConcept === 'ar-vs-ma' && (
              <div className="space-y-6">
                <div className="bg-slate-800 rounded-lg p-6 border-2 border-purple-600">
                  <h2 className="text-purple-300 text-2xl font-bold mb-4">AR vs MA: Quick Comparison</h2>
                  
                  <div className="grid grid-cols-2 gap-6">
                    <div className="bg-slate-900 p-4 rounded border-l-4 border-blue-500">
                      <h3 className="text-blue-300 font-bold mb-3">AR(1)</h3>
                      <div className="text-xs text-slate-300 space-y-2">
                        <div><strong>Formula:</strong> x(t) = φ×x(t-1) + ε(t)</div>
                        <div><strong>Memory:</strong> Depends on own past values</div>
                        <div><strong>Duration:</strong> Shocks last forever (decay slowly)</div>
                        <div><strong>ACF:</strong> Decays exponentially</div>
                        <div><strong>Real world:</strong> Stock prices, temperatures, smooth trends</div>
                      </div>
                    </div>

                    <div className="bg-slate-900 p-4 rounded border-l-4 border-green-500">
                      <h3 className="text-green-300 font-bold mb-3">MA(1)</h3>
                      <div className="text-xs text-slate-300 space-y-2">
                        <div><strong>Formula:</strong> x(t) = ε(t) + θ×ε(t-1)</div>
                        <div><strong>Memory:</strong> Depends on past shocks (errors)</div>
                        <div><strong>Duration:</strong> Shocks last 1 lag, then gone</div>
                        <div><strong>ACF:</strong> Cuts off after lag 1</div>
                        <div><strong>Real world:</strong> Measurement errors, one-time bumps</div>
                      </div>
                    </div>
                  </div>

                  <div className="bg-slate-800 rounded-lg p-4 border border-slate-700 mt-6">
                    <h3 className="text-slate-300 font-bold mb-3">How to Tell Them Apart</h3>
                    <div className="text-xs text-slate-300 space-y-2">
                      <div><strong>AR:</strong> Look for ACF that slowly decays over many lags</div>
                      <div><strong>MA:</strong> Look for ACF that spikes at lag 1 then drops to zero</div>
                      <div><strong>ARMA:</strong> When you see both patterns mixed together</div>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}