const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

export async function fetchSummary() {
  try {
    const res = await fetch(`${API_BASE}/dashboard/summary`);
    if (res.ok) return await res.json();
  } catch (e) {
    console.warn("Backend API offline, utilizing simulation fallback:", e);
  }
  return {
    system_status: "healthy",
    operational_mode: "SIMULATION MODE",
    cluster_name: "Minikube (Local)",
    environment: "development",
    uptime_seconds: 1450.0,
    active_pods: 6,
    healthy_services_count: 3,
    total_services_count: 3,
    anomalies_detected: 0,
    remediations_executed: 0,
    grafana_url: "http://localhost:3000"
  };
}

export async function fetchServices() {
  try {
    const res = await fetch(`${API_BASE}/services`);
    if (res.ok) return await res.json();
  } catch (e) {
    console.warn("Backend API offline for services:", e);
  }
  return [
    {
      service_name: "auth-service",
      status: "healthy",
      latency_ms: 42.0,
      error_rate_pct: 0.1,
      cpu_pct: 14.5,
      memory_pct: 38.0,
      pods_healthy: 2,
      pods_total: 2,
      restart_count: 0
    },
    {
      service_name: "order-service",
      status: "healthy",
      latency_ms: 82.0,
      error_rate_pct: 0.2,
      cpu_pct: 18.0,
      memory_pct: 42.0,
      pods_healthy: 2,
      pods_total: 2,
      restart_count: 0
    },
    {
      service_name: "inventory-service",
      status: "healthy",
      latency_ms: 55.0,
      error_rate_pct: 0.1,
      cpu_pct: 16.0,
      memory_pct: 40.0,
      pods_healthy: 2,
      pods_total: 2,
      restart_count: 0
    }
  ];
}

export async function triggerChaos(action, target_service, extra = {}) {
  const url = `${API_BASE}/chaos/${action}`;
  try {
    const res = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ target_service, ...extra })
    });
    if (res.ok) return await res.json();
  } catch (e) {
    console.warn("Chaos API error:", e);
  }
  return { status: "simulated", action, target_service };
}

export async function fetchEvents() {
  try {
    const res = await fetch(`${API_BASE}/events`);
    if (res.ok) return await res.json();
  } catch (e) {}
  return [
    { timestamp: new Date().toISOString(), level: "info", message: "CloudPulse Control Plane operational." }
  ];
}
