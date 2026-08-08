import React, { useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';

export default function LiveMetricsChart({ data }) {
  const [selectedService, setSelectedService] = useState('order-service');
  const [timeRange, setTimeRange] = useState('15m');

  return (
    <div class="glass-panel p-6 rounded-xl border border-gray-800">
      <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
        <div>
          <h3 class="text-base font-bold text-white">Live Telemetry & Performance Metrics</h3>
          <p class="text-xs text-gray-400">Prometheus Real-Time Scraping Data</p>
        </div>

        <div class="flex items-center gap-3">
          <select 
            value={selectedService}
            onChange={(e) => setSelectedService(e.target.value)}
            class="bg-gray-900 text-gray-200 border border-gray-700 text-xs rounded-lg px-3 py-1.5 focus:outline-none focus:border-indigo-500 font-mono"
          >
            <option value="auth-service">Auth Service</option>
            <option value="order-service">Order Service</option>
            <option value="inventory-service">Inventory Service</option>
          </select>

          <div class="flex items-center bg-gray-900 rounded-lg p-1 border border-gray-800 text-xs">
            {['5m', '15m', '30m', '1h'].map((t) => (
              <button
                key={t}
                onClick={() => setTimeRange(t)}
                class={`px-2.5 py-1 rounded font-medium transition-all ${
                  timeRange === t ? 'bg-indigo-600 text-white' : 'text-gray-400 hover:text-white'
                }`}
              >
                {t}
              </button>
            ))}
          </div>
        </div>
      </div>

      <div class="h-64 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1F2937" />
            <XAxis dataKey="time" stroke="#6B7280" tick={{ fontSize: 11 }} />
            <YAxis stroke="#6B7280" tick={{ fontSize: 11 }} />
            <Tooltip 
              contentStyle={{ backgroundColor: '#111827', borderColor: '#374151', borderRadius: '8px', fontSize: '12px' }}
            />
            <Legend wrapperStyle={{ fontSize: '12px', paddingTop: '10px' }} />
            <Line type="monotone" dataKey="latencyP95" name="Latency P95 (ms)" stroke="#6366F1" strokeWidth={2} dot={false} />
            <Line type="monotone" dataKey="latencyMean" name="Latency Mean (ms)" stroke="#10B981" strokeDasharray="5 5" dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
