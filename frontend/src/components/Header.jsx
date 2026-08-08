import React from 'react';

export default function Header({ summary }) {
  const isReal = summary.operational_mode === 'REAL MODE';
  const isHealthy = summary.system_status === 'healthy';

  return (
    <header class="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-6 border-b border-gray-800">
      <div>
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 to-indigo-400 flex items-center justify-center text-white font-bold text-xl shadow-lg shadow-indigo-500/30">
            CP
          </div>
          <div>
            <h1 class="text-2xl font-extrabold text-white tracking-tight flex items-center gap-2">
              CloudPulse
              <span class="text-xs font-mono font-medium px-2 py-0.5 rounded bg-gray-800 text-gray-400 border border-gray-700">
                v0.1.0
              </span>
            </h1>
            <p class="text-xs text-gray-400">Self-Healing Cloud Platform & Control Plane</p>
          </div>
        </div>
      </div>

      <div class="flex items-center gap-3 flex-wrap">
        <!-- System Status Badge -->
        <div class={`flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-semibold border ${
          isHealthy 
            ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30' 
            : 'bg-rose-500/10 text-rose-400 border-rose-500/30 animate-pulse'
        }`}>
          <span class={`w-2 h-2 rounded-full ${isHealthy ? 'bg-emerald-400' : 'bg-rose-400'}`}></span>
          {isHealthy ? 'SYSTEM HEALTHY' : 'DEGRADATION DETECTED'}
        </div>

        <!-- Operational Mode Badge -->
        <div class={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-mono font-medium border ${
          isReal 
            ? 'bg-indigo-500/10 text-indigo-400 border-indigo-500/30' 
            : 'bg-amber-500/10 text-amber-400 border-amber-500/30'
        }`}>
          <span>{isReal ? '🟢' : '⚡'}</span>
          {summary.operational_mode}
        </div>

        <!-- Open Grafana Link Button -->
        <a 
          href={summary.grafana_url || "http://localhost:3000"} 
          target="_blank" 
          rel="noopener noreferrer"
          class="px-4 py-2 bg-gray-800 hover:bg-gray-700 text-gray-200 text-xs font-semibold rounded-lg border border-gray-700 transition-all flex items-center gap-2 shadow-sm"
        >
          <svg class="w-4 h-4 text-orange-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
          </svg>
          Open Grafana
        </a>
      </div>
    </header>
  );
}
