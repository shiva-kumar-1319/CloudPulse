import React from 'react';

export default function RemediationPanel({ remediations }) {
  return (
    <div class="glass-panel p-6 rounded-xl border border-gray-800">
      <h3 class="text-base font-bold text-white mb-4">Recent Kubernetes Self-Healing Remediations</h3>
      
      <div class="overflow-x-auto">
        <table class="w-full text-left text-xs font-mono">
          <thead class="bg-gray-900/80 text-gray-400 border-b border-gray-800">
            <tr>
              <th class="p-2.5">Service</th>
              <th class="p-2.5">Action</th>
              <th class="p-2.5">Score</th>
              <th class="p-2.5">Status</th>
              <th class="p-2.5">Time</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-800/60 text-gray-300">
            {remediations.length === 0 ? (
              <tr>
                <td colSpan="5" class="p-4 text-center text-gray-500 italic">
                  No remediation actions executed yet. System baseline nominal.
                </td>
              </tr>
            ) : (
              remediations.map((rem, i) => (
                <tr key={i} class="hover:bg-gray-900/40">
                  <td class="p-2.5 font-bold uppercase">{rem.target_service}</td>
                  <td class="p-2.5 text-indigo-400">{rem.action}</td>
                  <td class="p-2.5 font-bold text-amber-400">{rem.anomaly_score.toFixed(2)}</td>
                  <td class="p-2.5 text-emerald-400 font-bold">{rem.status}</td>
                  <td class="p-2.5 text-gray-500">{new Date(rem.timestamp).toLocaleTimeString()}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
