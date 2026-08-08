# CloudPulse Custom React Control Plane Frontend

This directory contains the custom **React + Vite + Tailwind CSS** single-page web dashboard for CloudPulse. It serves as the **Application Control Plane & Self-Healing Demo Interface**.

---

## 🎨 Features
- **Global System Status Header**: Displays cluster name, active pods, operational mode (`🟢 REAL MODE` vs `⚡ SIMULATION MODE`), and `[ Open Grafana ]` link button.
- **Service Health Cards**: Microservices latency (P95), HTTP error rate %, CPU %, Memory %, healthy pod counts, restart counts, and last remediation timestamp.
- **Live Metrics Charts**: Interactive Recharts telemetry visualization.
- **ML Anomaly Detection Panel**: Displays real-time Isolation Forest score, status badge, and feature contributions.
- **Self-Healing Event Timeline**: Chronological event log stream.
- **Chaos Control Panel**: Interactive buttons (`Kill Pod`, `Inject Latency`, `Inject Errors`) invoking backend `/api/chaos/*` endpoints safely.

---

## 🚀 Local Development
```bash
cd frontend/
npm install
npm run dev
```
Open **`http://localhost:5173`** in your browser.
