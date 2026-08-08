import React, { useState } from 'react';
import { triggerChaos } from '../services/api';

export default function ChaosControlPanel({ onChaosTriggered }) {
  const [targetService, setTargetService] = useState('order-service');
  const [loading, setLoading] = useState(false);

  const handleChaosAction = async (action, extra = {}) => {
    setLoading(true);
    await triggerChaos(action, targetService, extra);
    setLoading(false);
    if (onChaosTriggered) onChaosTriggered(action, targetService);
  };

  return (
    <div class="glass-panel p-6 rounded-xl border border-gray-800">
      <div class="flex items-center justify-between mb-2">
        <h3 class="text-base font-bold text-white">Chaos Engineering Control Panel</h3>
        <span class="text-[10px] font-bold tracking-wider text-amber-400 bg-amber-500/10 px-2 py-0.5 rounded border border-amber-500/30">
          DEVELOPMENT / TEST ONLY
        </span>
      </div>
      <p class="text-xs text-gray-400 mb-4">
        Inject controlled chaos faults into microservices to trigger Prometheus metric spikes and validate automated self-healing.
      </p>

      <div class="mb-4">
        <label class="block text-xs font-medium text-gray-400 mb-1">Target Service</label>
        <select 
          value={targetService} 
          onChange={(e) => setTargetService(e.target.value)}
          class="w-full bg-gray-900 border border-gray-700 text-gray-200 text-xs rounded-lg p-2.5 font-mono focus:outline-none focus:border-indigo-500"
        >
          <option value="order-service">Order Service</option>
          <option value="auth-service">Auth Service</option>
          <option value="inventory-service">Inventory Service</option>
        </select>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
        <button
          disabled={loading}
          onClick={() => handleChaosAction('pod')}
          class="flex items-center justify-center gap-2 p-3 bg-rose-500/10 hover:bg-rose-500/20 text-rose-300 border border-rose-500/30 rounded-xl text-xs font-semibold transition-all disabled:opacity-50"
        >
          <span>💀</span> Kill Pod
        </button>

        <button
          disabled={loading}
          onClick={() => handleChaosAction('latency', { seconds: 5.0 })}
          class="flex items-center justify-center gap-2 p-3 bg-amber-500/10 hover:bg-amber-500/20 text-amber-300 border border-amber-500/30 rounded-xl text-xs font-semibold transition-all disabled:opacity-50"
        >
          <span>⏳</span> Inject 5s Latency
        </button>

        <button
          disabled={loading}
          onClick={() => handleChaosAction('errors', { rate: 0.5 })}
          class="flex items-center justify-center gap-2 p-3 bg-amber-500/10 hover:bg-amber-500/20 text-amber-300 border border-amber-500/30 rounded-xl text-xs font-semibold transition-all disabled:opacity-50"
        >
          <span>💥</span> Inject 50% Errors
        </button>
      </div>
    </div>
  );
}
