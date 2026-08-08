import React from 'react';

export default function SystemSummaryCard({ summary }) {
  return (
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <div class="glass-panel p-4 rounded-xl border border-gray-800">
        <div class="text-xs text-gray-400 font-medium">Cluster</div>
        <div class="text-lg font-bold text-white mt-1">{summary.cluster_name}</div>
        <div class="text-xs text-gray-500 mt-0.5">Env: {summary.environment}</div>
      </div>

      <div class="glass-panel p-4 rounded-xl border border-gray-800">
        <div class="text-xs text-gray-400 font-medium">Active Pods</div>
        <div class="text-lg font-bold text-white mt-1">{summary.active_pods} / 6</div>
        <div class="text-xs text-emerald-400 mt-0.5">{summary.healthy_services_count} Services Healthy</div>
      </div>

      <div class="glass-panel p-4 rounded-xl border border-gray-800">
        <div class="text-xs text-gray-400 font-medium">ML Anomalies Detected</div>
        <div class="text-lg font-bold text-indigo-400 mt-1">{summary.anomalies_detected}</div>
        <div class="text-xs text-gray-500 mt-0.5">Isolation Forest Engine</div>
      </div>

      <div class="glass-panel p-4 rounded-xl border border-gray-800">
        <div class="text-xs text-gray-400 font-medium">Remediations Executed</div>
        <div class="text-lg font-bold text-emerald-400 mt-1">{summary.remediations_executed}</div>
        <div class="text-xs text-gray-500 mt-0.5">Kubernetes Self-Healing</div>
      </div>
    </div>
  );
}
