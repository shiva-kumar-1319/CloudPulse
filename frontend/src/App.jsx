import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import SystemSummaryCard from './components/SystemSummaryCard';
import ServiceHealthCard from './components/ServiceHealthCard';
import LiveMetricsChart from './components/LiveMetricsChart';
import AnomalyPanel from './components/AnomalyPanel';
import SelfHealingTimeline from './components/SelfHealingTimeline';
import ChaosControlPanel from './components/ChaosControlPanel';
import RemediationPanel from './components/RemediationPanel';
import { fetchSummary, fetchServices, fetchEvents } from './services/api';

export default function App() {
  const [summary, setSummary] = useState({
    system_status: "healthy",
    operational_mode: "SIMULATION MODE",
    cluster_name: "Minikube (Local)",
    environment: "development",
    active_pods: 6,
    healthy_services_count: 3,
    total_services_count: 3,
    anomalies_detected: 0,
    remediations_executed: 0,
    grafana_url: "http://localhost:3000"
  });

  const [services, setServices] = useState([]);
  const [events, setEvents] = useState([]);
  const [chartData, setChartData] = useState(
    Array.from({ length: 15 }, (_, i) => ({
      time: `${15 - i}s ago`,
      latencyP95: 85 + Math.floor(Math.random() * 10),
      latencyMean: 45 + Math.floor(Math.random() * 5),
    }))
  );

  const refreshData = async () => {
    const sum = await fetchSummary();
    const svcs = await fetchServices();
    const evts = await fetchEvents();

    setSummary(sum);
    setServices(svcs);
    setEvents(evts);

    // Update telemetry graph
    const latestOrder = svcs.find(s => s.service_name === 'order-service');
    if (latestOrder) {
      setChartData(prev => [
        ...prev.slice(1),
        {
          time: new Date().toLocaleTimeString(),
          latencyP95: latestOrder.latency_ms,
          latencyMean: Math.round(latestOrder.latency_ms * 0.5),
        }
      ]);
    }
  };

  useEffect(() => {
    refreshData();
    const interval = setInterval(refreshData, 3000);
    return () => clearInterval(interval);
  }, []);

  const handleChaosTriggered = (action, target) => {
    refreshData();
  };

  return (
    <div class="min-h-screen bg-[#0B0F19] text-gray-100 p-6 md:p-10 space-y-6">
      <!-- Top Header Navigation -->
      <Header summary={summary} />

      <!-- KPI Summary Row -->
      <SystemSummaryCard summary={summary} />

      <!-- Microservice Health Cards -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-5">
        {services.map((svc) => (
          <ServiceHealthCard key={svc.service_name} service={svc} />
        ))}
      </div>

      <!-- Live Telemetry & ML Anomaly Breakdown -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <LiveMetricsChart data={chartData} />
        <AnomalyPanel currentAnomaly={null} />
      </div>

      <!-- Self-Healing Event Timeline & Chaos Control Panel -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ChaosControlPanel onChaosTriggered={handleChaosTriggered} />
        <SelfHealingTimeline events={events} />
      </div>

      <!-- Recent Remediation Actions History -->
      <RemediationPanel remediations={[]} />
    </div>
  );
}
