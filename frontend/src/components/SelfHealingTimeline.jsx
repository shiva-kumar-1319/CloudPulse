import React from 'react';

export default function SelfHealingTimeline({ events }) {
  return (
    <div class="glass-panel p-6 rounded-xl border border-gray-800 flex flex-col h-full">
      <h3 class="text-base font-bold text-white mb-4">Real-Time Self-Healing Timeline</h3>
      
      <div class="flex-1 overflow-y-auto max-h-72 space-y-3 font-mono text-xs pr-2">
        {events.map((evt, idx) => (
          <div key={idx} class="flex items-start gap-3 p-2.5 rounded-lg bg-gray-900/60 border border-gray-800/80">
            <span class="text-gray-500 shrink-0">{new Date(evt.timestamp).toLocaleTimeString()}</span>
            <span class={`font-medium ${
              evt.level === 'danger' ? 'text-rose-400' :
              evt.level === 'warning' ? 'text-amber-400' :
              evt.level === 'success' ? 'text-emerald-400' : 'text-gray-300'
            }`}>
              {evt.message}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
