import React from 'react';

export default function AnomalyPanel({ currentAnomaly }) {
  const isAnomaly = currentAnomaly && currentAnomaly.anomaly_score >= 0.75;

  return (
    <div class="glass-panel p-6 rounded-xl border border-gray-800">
      <div class="flex items-center justify-between mb-4">
        <h3 class="text-base font-bold text-white">ML Anomaly Detection (Isolation Forest)</h3>
        <span class="text-xs font-mono text-gray-500">Model: Isolation Forest v1</span>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
        <div class="bg-gray-900/80 p-4 rounded-xl border border-gray-800">
          <div class="text-xs text-gray-400">Target Service</div>
          <div class="text-base font-bold text-white mt-1 font-mono uppercase">
            {currentAnomaly ? currentAnomaly.target_service : 'order-service'}
          </div>
        </div>

        <div class="bg-gray-900/80 p-4 rounded-xl border border-gray-800">
          <div class="text-xs text-gray-400">Anomaly Score</div>
          <div class={`text-2xl font-extrabold mt-1 font-mono ${isAnomaly ? 'text-rose-400' : 'text-indigo-400'}`}>
            {currentAnomaly ? currentAnomaly.anomaly_score.toFixed(2) : '0.13'}
          </div>
        </div>

        <div class="bg-gray-900/80 p-4 rounded-xl border border-gray-800">
          <div class="text-xs text-gray-400">Detection Status</div>
          <div class={`text-sm font-bold mt-1.5 ${isAnomaly ? 'text-rose-400 animate-pulse' : 'text-emerald-400'}`}>
            {isAnomaly ? '🔴 DEGRADATION DETECTED' : '🟢 HEALTHY BASELINE'}
          </div>
        </div>
      </div>

      <div class="bg-gray-900/50 p-4 rounded-xl border border-gray-800/60 text-xs">
        <div class="font-semibold text-gray-300 mb-2">Feature Weight Contributions:</div>
        <div class="grid grid-cols-3 gap-2 font-mono text-gray-400">
          <div>Latency P95: <span class={isAnomaly ? "text-rose-400 font-bold" : "text-gray-200"}>HIGH</span></div>
          <div>Error Rate: <span class={isAnomaly ? "text-rose-400 font-bold" : "text-gray-200"}>HIGH</span></div>
          <div>CPU Usage: <span class="text-gray-200">MEDIUM</span></div>
        </div>
      </div>
    </div>
  );
}
