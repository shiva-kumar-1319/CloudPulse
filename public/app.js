// CloudPulse Web Dashboard & Simulation Logic

document.addEventListener('DOMContentLoaded', () => {
    // State variables
    let currentMetrics = {
        latencyMean: 45, // ms
        latencyP95: 85,  // ms
        errorRate: 0.2,  // %
        requestRate: 48, // req/s
        mlScore: 0.13,
        status: 'healthy' // 'healthy', 'degraded', 'anomaly'
    };

    let logHistory = [];

    // Initialize Chart.js Graphs
    const ctxLatency = document.getElementById('chart-latency').getContext('2d');
    const ctxML = document.getElementById('chart-ml').getContext('2d');

    const initialLabels = Array.from({length: 15}, (_, i) => `${15 - i}s ago`);
    
    // Latency Chart
    const chartLatency = new Chart(ctxLatency, {
        type: 'line',
        data: {
            labels: initialLabels,
            datasets: [
                {
                    label: 'Latency P95 (ms)',
                    data: Array(15).fill(85),
                    borderColor: '#6366F1',
                    backgroundColor: 'rgba(99, 102, 241, 0.1)',
                    fill: true,
                    tension: 0.4
                },
                {
                    label: 'Latency Mean (ms)',
                    data: Array(15).fill(45),
                    borderColor: '#10B981',
                    borderDash: [5, 5],
                    fill: false,
                    tension: 0.4
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { labels: { color: '#9CA3AF' } } },
            scales: {
                x: { ticks: { color: '#6B7280' }, grid: { color: 'rgba(255,255,255,0.05)' } },
                y: { ticks: { color: '#6B7280' }, grid: { color: 'rgba(255,255,255,0.05)' } }
            }
        }
    });

    // ML Anomaly Score Chart
    const chartML = new Chart(ctxML, {
        type: 'line',
        data: {
            labels: initialLabels,
            datasets: [
                {
                    label: 'ML Isolation Forest Score',
                    data: Array(15).fill(0.13),
                    borderColor: '#A5B4FC',
                    backgroundColor: 'rgba(165, 180, 252, 0.15)',
                    fill: true,
                    tension: 0.3
                },
                {
                    label: 'Anomaly Threshold (0.75)',
                    data: Array(15).fill(0.75),
                    borderColor: '#EF4444',
                    borderDash: [4, 4],
                    pointRadius: 0,
                    fill: false
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { labels: { color: '#9CA3AF' } } },
            scales: {
                x: { ticks: { color: '#6B7280' }, grid: { color: 'rgba(255,255,255,0.05)' } },
                y: { min: 0, max: 1.0, ticks: { color: '#6B7280' }, grid: { color: 'rgba(255,255,255,0.05)' } }
            }
        }
    });

    // UI Elements
    const kpiLatency = document.getElementById('kpi-latency');
    const badgeLatency = document.getElementById('badge-latency');
    const kpiError = document.getElementById('kpi-error-rate');
    const badgeError = document.getElementById('badge-error');
    const kpiML = document.getElementById('kpi-ml-score');
    const badgeML = document.getElementById('badge-ml-score');
    const globalDot = document.getElementById('global-status-dot');
    const globalText = document.getElementById('global-status-text');
    const nodeOrder = document.getElementById('status-order-node');
    const terminalLogs = document.getElementById('remediation-logs');

    function addLog(msg, type = 'info') {
        const time = new Date().toLocaleTimeString();
        const line = document.createElement('div');
        line.className = `log-line ${type}`;
        line.innerText = `[${time}] ${msg}`;
        terminalLogs.appendChild(line);
        terminalLogs.scrollTop = terminalLogs.scrollHeight;
    }

    function updateMetricsUI() {
        kpiLatency.innerText = `${Math.round(currentMetrics.latencyP95)} ms`;
        badgeLatency.innerText = `${Math.round(currentMetrics.latencyP95)} ms`;
        
        kpiError.innerText = `${currentMetrics.errorRate.toFixed(1)}%`;
        badgeError.innerText = `${currentMetrics.errorRate.toFixed(1)}%`;

        kpiML.innerText = currentMetrics.mlScore.toFixed(2);
        badgeML.innerText = currentMetrics.mlScore.toFixed(2);

        // Status update
        if (currentMetrics.mlScore >= 0.75) {
            globalDot.className = 'status-dot anomaly';
            globalText.innerText = 'Anomaly Detected';
            badgeML.className = 'kpi-badge danger';
            badgeLatency.className = 'kpi-badge danger';
            badgeError.className = 'kpi-badge danger';
            nodeOrder.className = 'node-status failed';
        } else if (currentMetrics.mlScore >= 0.50) {
            globalDot.className = 'status-dot degraded';
            globalText.innerText = 'System Degraded';
            badgeML.className = 'kpi-badge warning';
            nodeOrder.className = 'node-status degraded';
        } else {
            globalDot.className = 'status-dot healthy';
            globalText.innerText = 'System Healthy';
            badgeML.className = 'kpi-badge emerald';
            badgeLatency.className = 'kpi-badge emerald';
            badgeError.className = 'kpi-badge emerald';
            nodeOrder.className = 'node-status healthy';
        }

        // Update Charts
        chartLatency.data.datasets[0].data.shift();
        chartLatency.data.datasets[0].data.push(currentMetrics.latencyP95);
        chartLatency.data.datasets[1].data.shift();
        chartLatency.data.datasets[1].data.push(currentMetrics.latencyMean);
        chartLatency.update();

        chartML.data.datasets[0].data.shift();
        chartML.data.datasets[0].data.push(currentMetrics.mlScore);
        chartML.update();
    }

    // Live Metrics Tick Loop
    setInterval(() => {
        if (currentMetrics.status === 'healthy') {
            currentMetrics.latencyMean = 40 + (Math.random() * 10 - 5);
            currentMetrics.latencyP95 = 80 + (Math.random() * 15 - 7);
            currentMetrics.errorRate = 0.2 + (Math.random() * 0.1);
            currentMetrics.mlScore = 0.12 + (Math.random() * 0.04);
        }
        updateMetricsUI();
    }, 2000);

    // Chaos Handlers
    document.getElementById('btn-chaos-kill').addEventListener('click', () => {
        addLog('🔥 [CHAOS] Pod termination injected into order-service.', 'danger');
        currentMetrics.status = 'anomaly';
        currentMetrics.latencyP95 = 9800;
        currentMetrics.errorRate = 45.0;
        currentMetrics.mlScore = 0.96;
        updateMetricsUI();

        setTimeout(() => triggerAutomatedRemediation('order-service', 'restart_pod'), 3000);
    });

    document.getElementById('btn-chaos-latency').addEventListener('click', () => {
        addLog('⏳ [CHAOS] Artificial 5.0s response latency injected into order-service.', 'warning');
        currentMetrics.status = 'anomaly';
        currentMetrics.latencyP95 = 5200;
        currentMetrics.latencyMean = 3800;
        currentMetrics.mlScore = 0.88;
        updateMetricsUI();

        setTimeout(() => triggerAutomatedRemediation('order-service', 'scale_deployment'), 3500);
    });

    document.getElementById('btn-chaos-errors').addEventListener('click', () => {
        addLog('💥 [CHAOS] 50% HTTP 500 error rate injected into order-service.', 'warning');
        currentMetrics.status = 'anomaly';
        currentMetrics.errorRate = 50.0;
        currentMetrics.mlScore = 0.91;
        updateMetricsUI();

        setTimeout(() => triggerAutomatedRemediation('order-service', 'restart_pod'), 3000);
    });

    // Reset Baseline
    document.getElementById('btn-reset-baseline').addEventListener('click', () => {
        currentMetrics = {
            latencyMean: 45,
            latencyP95: 85,
            errorRate: 0.2,
            requestRate: 48,
            mlScore: 0.13,
            status: 'healthy'
        };
        updateMetricsUI();
        addLog('[BASELINE] System baseline metrics manually restored.', 'success');
    });

    // E2E Simulation Demo Cycle
    document.getElementById('btn-run-simulation').addEventListener('click', async () => {
        addLog('[SIMULATION] Initiating E2E CloudPulse Self-Healing Demo Cycle...', 'info');
        
        // Step 1: Normal Baseline
        currentMetrics.status = 'healthy';
        updateMetricsUI();
        await new Promise(r => setTimeout(r, 2000));

        // Step 2: Fault Injection
        addLog('🔥 [STEP 2] Injecting chaos failure into order-service...', 'warning');
        currentMetrics.status = 'anomaly';
        currentMetrics.latencyP95 = 9800;
        currentMetrics.errorRate = 45.0;
        currentMetrics.mlScore = 0.97;
        updateMetricsUI();
        await new Promise(r => setTimeout(r, 3500));

        // Step 3 & 4: Remediation
        triggerAutomatedRemediation('order-service', 'restart_pod');
    });

    function triggerAutomatedRemediation(service, action) {
        addLog(`🚨 [ML-ENGINE] Isolation Forest Anomaly Alert! Score: ${currentMetrics.mlScore.toFixed(2)} (Threshold: 0.75)`, 'danger');
        addLog(`🛡️ [GUARDRAIL] Evaluating safety policies for '${service}'... PASS`, 'info');
        addLog(`⚡ [REMEDIATION] Executing action '${action}' via Kubernetes API...`, 'warning');

        setTimeout(() => {
            currentMetrics = {
                latencyMean: 42,
                latencyP95: 82,
                errorRate: 0.1,
                requestRate: 48,
                mlScore: 0.12,
                status: 'healthy'
            };
            updateMetricsUI();
            addLog(`✅ [RECOVERY] Target pod recycled. Readiness probe PASSED. System fully recovered!`, 'success');
        }, 2500);
    }

    document.getElementById('btn-clear-logs').addEventListener('click', () => {
        terminalLogs.innerHTML = '';
    });
});
