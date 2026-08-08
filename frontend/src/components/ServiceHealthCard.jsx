import React from 'react';

export default function ServiceHealthCard({ service }) {
  const isHealthy = service.status === 'healthy';

  return (
    <div class="glass-panel p-5 rounded-xl border border-gray-800 hover:border-gray-700 transition-all">
      <div class="flex items-center justify-between mb-4">
        <div>
          <h3 class="text-base font-bold text-white uppercase tracking-wide">{service.service_name}</h3>
          <span class="text-xs text-gray-500 font-mono">Pods: {service.pods_healthy}/{service.pods_total}</span>
        </div>
        <span class={`px-2.5 py-1 rounded-full text-xs font-bold ${
          isHealthy 
            ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30' 
            : 'bg-rose-500/15 text-rose-400 border border-rose-500/30 animate-pulse'
        }`}>
          {isHealthy ? '🟢 HEALTHY' : '🔴 DEGRADED'}
        </span>
      </div>

      <div class="grid grid-cols-2 gap-3 text-xs mb-3">
        <div class="bg-gray-900/60 p-2.5 rounded-lg border border-gray-800/80">
          <div class="text-gray-400">Latency P95</div>
          <div class={`text-sm font-mono font-bold ${service.latency_ms > 500 ? 'text-rose-400' : 'text-gray-100'}`}>
            {service.latency_ms} ms
          </div>
        </div>

        <div class="bg-gray-900/60 p-2.5 rounded-lg border border-gray-800/80">
          <div class="text-gray-400">Error Rate</div>
          <div class={`text-sm font-mono font-bold ${service.error_rate_pct > 5.0 ? 'text-rose-400' : 'text-gray-100'}`}>
            {service.error_rate_pct}%
          </div>
        </div>

        <div class="bg-gray-900/60 p-2.5 rounded-lg border border-gray-800/80">
          <div class="text-gray-400">CPU Usage</div>
          <div class="text-sm font-mono font-bold text-gray-100">{service.cpu_pct}%</div>
        </div>

        <div class="bg-gray-900/60 p-2.5 rounded-lg border border-gray-800/80">
          <div class="text-gray-400">Memory Usage</div>
          <div class="text-sm font-mono font-bold text-gray-100">{service.memory_pct}%</div>
        </div>
      </div>

      <div class="flex justify-between items-center text-[11px] text-gray-500 pt-2 border-t border-gray-800/60 font-mono">
        <span>Restarts: {service.restart_count}</span>
        <span>Last Fix: {service.last_remediation_at ? new Date(service.last_remediation_at).toLocaleTimeString() : 'None'}</span>
      </div>
    </div>
  );
}
