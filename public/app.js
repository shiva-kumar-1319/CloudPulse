// CloudPulse dashboard — handles the simulation state machine, chart updates, and all the interactive bits
// Written by Shiva Kumar

document.addEventListener('DOMContentLoaded', () => {
    // Holds all the current metric values and simulation state
    const state = {
        status: 'healthy', // 'healthy', 'degraded', 'recovering'
        metrics: {
            latencyMean: 45,   // ms
            latencyP95: 85,    // ms
            errorRate: 0.2,    // %
            requestRate: 48,   // req/s
            cpuUsage: 24,      // millicores
            memoryUsage: 78,   // MiB
            restarts: 0,
            mlScore: 0.13
        },
        baseline: {
            latencyMean: 45,
            latencyP95: 85,
            errorRate: 0.2,
            requestRate: 48,
            cpuUsage: 24,
            memoryUsage: 78,
            restarts: 0,
            mlScore: 0.13
        },
        remediationCooldown: false,
        activeChaos: null
    };

    // UI Element References
    const kpiRequests = document.getElementById('kpi-requests');
    const badgeRequests = document.getElementById('badge-requests');
    const kpiLatency = document.getElementById('kpi-latency');
    const badgeLatency = document.getElementById('badge-latency');
    const kpiError = document.getElementById('kpi-error-rate');
    const badgeError = document.getElementById('badge-error');
    const kpiML = document.getElementById('kpi-ml-score');
    const badgeML = document.getElementById('badge-ml-score');
    const globalDot = document.getElementById('global-status-dot');
    const globalText = document.getElementById('global-status-text');
    const terminalLogs = document.getElementById('remediation-logs');

    // Pod Elements
    const badgePodOrder = document.getElementById('badge-pod-order');
    const valOrderCpu = document.getElementById('val-order-cpu');
    const valOrderMem = document.getElementById('val-order-mem');
    const valOrderRestarts = document.getElementById('val-order-restarts');
    const statusOrderNode = document.getElementById('status-order-node');

    // Chart.js Contexts
    const ctxLatency = document.getElementById('chart-latency').getContext('2d');
    const ctxML = document.getElementById('chart-ml').getContext('2d');

    const timeWindowSize = 15;
    const initialLabels = Array.from({ length: timeWindowSize }, (_, i) => `${timeWindowSize - 1 - i}s ago`);
    
    // Latency Chart Configuration
    const chartLatency = new Chart(ctxLatency, {
        type: 'line',
        data: {
            labels: initialLabels,
            datasets: [
                {
                    label: 'Latency P95 (ms)',
                    data: Array(timeWindowSize).fill(85),
                    borderColor: '#6366f1',
                    backgroundColor: 'rgba(99, 102, 241, 0.12)',
                    fill: true,
                    tension: 0.35,
                    borderWidth: 2
                },
                {
                    label: 'Latency Mean (ms)',
                    data: Array(timeWindowSize).fill(45),
                    borderColor: '#06b6d4',
                    borderDash: [4, 4],
                    fill: false,
                    tension: 0.35,
                    borderWidth: 1.8
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: { duration: 400 },
            plugins: {
                legend: {
                    labels: { color: '#94a3b8', font: { family: 'Inter', size: 11 } }
                }
            },
            scales: {
                x: {
                    ticks: { color: '#64748b', font: { size: 10 } },
                    grid: { color: 'rgba(255, 255, 255, 0.04)' }
                },
                y: {
                    suggestedMin: 0,
                    suggestedMax: 200,
                    ticks: { color: '#64748b', font: { size: 10 } },
                    grid: { color: 'rgba(255, 255, 255, 0.04)' }
                }
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
                    label: 'Isolation Forest Anomaly Score',
                    data: Array(timeWindowSize).fill(0.13),
                    borderColor: '#a5b4fc',
                    backgroundColor: 'rgba(165, 180, 252, 0.15)',
                    fill: true,
                    tension: 0.3,
                    borderWidth: 2
                },
                {
                    label: 'Anomaly Decision Boundary (0.75)',
                    data: Array(timeWindowSize).fill(0.75),
                    borderColor: '#f43f5e',
                    borderDash: [5, 5],
                    pointRadius: 0,
                    fill: false,
                    borderWidth: 1.5
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: { duration: 400 },
            plugins: {
                legend: {
                    labels: { color: '#94a3b8', font: { family: 'Inter', size: 11 } }
                }
            },
            scales: {
                x: {
                    ticks: { color: '#64748b', font: { size: 10 } },
                    grid: { color: 'rgba(255, 255, 255, 0.04)' }
                },
                y: {
                    min: 0.0,
                    max: 1.0,
                    ticks: { color: '#64748b', font: { size: 10 } },
                    grid: { color: 'rgba(255, 255, 255, 0.04)' }
                }
            }
        }
    });

    // Append to Terminal Log
    function addLog(msg, type = 'info') {
        const line = document.createElement('div');
        line.className = `log-line ${type}`;
        const timestamp = new Date().toISOString().substring(11, 19);
        line.textContent = `[${timestamp}] ${msg}`;
        terminalLogs.appendChild(line);
        terminalLogs.scrollTop = terminalLogs.scrollHeight;
    }

    // Calculate Multi-Dimensional ML Score
    function computeMLScore(p95, errorRate, cpu, mem) {
        let base = 0.12 + Math.random() * 0.04;
        if (p95 > 200) base += Math.min(0.45, (p95 - 200) / 1000);
        if (errorRate > 1.0) base += Math.min(0.40, errorRate / 50.0);
        if (cpu > 250) base += Math.min(0.20, (cpu - 250) / 500);
        if (mem > 180) base += Math.min(0.25, (mem - 180) / 200);
        return Math.min(0.98, parseFloat(base.toFixed(2)));
    }

    // Refresh UI & Chart Displays
    function updateUI() {
        const m = state.metrics;
        
        // Update KPI values
        kpiRequests.textContent = `${Math.round(m.requestRate)} req/s`;
        kpiLatency.textContent = `${Math.round(m.latencyP95)} ms`;
        badgeLatency.textContent = `${Math.round(m.latencyP95)} ms`;
        kpiError.textContent = `${m.errorRate.toFixed(1)}%`;
        badgeError.textContent = `${m.errorRate.toFixed(1)}%`;
        kpiML.textContent = m.mlScore.toFixed(2);
        badgeML.textContent = m.mlScore.toFixed(2);

        // Update badges color
        if (m.latencyP95 > 500) {
            badgeLatency.className = 'kpi-badge rose';
        } else if (m.latencyP95 > 150) {
            badgeLatency.className = 'kpi-badge amber';
        } else {
            badgeLatency.className = 'kpi-badge emerald';
        }

        if (m.errorRate > 5.0) {
            badgeError.className = 'kpi-badge rose';
        } else if (m.errorRate > 1.0) {
            badgeError.className = 'kpi-badge amber';
        } else {
            badgeError.className = 'kpi-badge emerald';
        }

        if (m.mlScore >= 0.75) {
            badgeML.className = 'kpi-badge rose';
        } else if (m.mlScore >= 0.40) {
            badgeML.className = 'kpi-badge amber';
        } else {
            badgeML.className = 'kpi-badge indigo';
        }

        // Global status
        if (state.status === 'healthy') {
            globalDot.className = 'status-dot healthy';
            globalText.textContent = 'System Healthy';
            globalText.style.color = 'var(--success)';
            statusOrderNode.className = 'node-status healthy';
            badgePodOrder.className = 'pod-badge running';
            badgePodOrder.textContent = 'Running';
        } else if (state.status === 'degraded') {
            globalDot.className = 'status-dot anomaly';
            globalText.textContent = 'Anomaly Detected';
            globalText.style.color = 'var(--danger)';
            statusOrderNode.className = 'node-status failing';
            badgePodOrder.className = 'pod-badge crashed';
            badgePodOrder.textContent = 'Degraded';
        } else if (state.status === 'recovering') {
            globalDot.className = 'status-dot degraded';
            globalText.textContent = 'Self-Healing Active';
            globalText.style.color = 'var(--warning)';
            statusOrderNode.className = 'node-status degraded';
            badgePodOrder.className = 'pod-badge restarting';
            badgePodOrder.textContent = 'Recycling';
        }

        // Pod telemetry stats
        if (valOrderCpu) valOrderCpu.textContent = `${Math.round(m.cpuUsage)}m / 500m`;
        if (valOrderMem) valOrderMem.textContent = `${Math.round(m.memoryUsage)} MiB / 256 MiB`;
        if (valOrderRestarts) valOrderRestarts.textContent = `${m.restarts}`;

        // Shift Chart Data
        chartLatency.data.datasets[0].data.shift();
        chartLatency.data.datasets[0].data.push(m.latencyP95);
        chartLatency.data.datasets[1].data.shift();
        chartLatency.data.datasets[1].data.push(m.latencyMean);
        chartLatency.update('none');

        chartML.data.datasets[0].data.shift();
        chartML.data.datasets[0].data.push(m.mlScore);
        chartML.update('none');
    }

    // Telemetry Ticker (Runs every 1.5 seconds)
    setInterval(() => {
        if (state.status === 'healthy') {
            // Apply slight organic jitter
            state.metrics.latencyMean = Math.max(30, 45 + (Math.random() * 8 - 4));
            state.metrics.latencyP95 = Math.max(70, 85 + (Math.random() * 14 - 7));
            state.metrics.errorRate = Math.max(0.05, 0.2 + (Math.random() * 0.1 - 0.05));
            state.metrics.requestRate = Math.max(40, 48 + (Math.random() * 6 - 3));
            state.metrics.cpuUsage = Math.max(18, 24 + (Math.random() * 4 - 2));
            state.metrics.memoryUsage = Math.max(70, 78 + (Math.random() * 3 - 1.5));
            state.metrics.mlScore = computeMLScore(state.metrics.latencyP95, state.metrics.errorRate, state.metrics.cpuUsage, state.metrics.memoryUsage);
        }
        updateUI();
    }, 1500);

    // Reset Baseline Handler
    function resetBaseline() {
        state.status = 'healthy';
        state.activeChaos = null;
        Object.assign(state.metrics, state.baseline);
        updateUI();
        addLog('[BASELINE] Operational parameters reset to healthy baseline.', 'success');
    }

    document.getElementById('btn-reset-baseline').addEventListener('click', resetBaseline);
    document.getElementById('btn-clear-logs').addEventListener('click', () => {
        terminalLogs.innerHTML = '';
        addLog('[CLEARED] Remediation logs cleared by operator.', 'info');
    });

    // Automated Self-Healing Simulation Execution
    function triggerSelfHealingWorkflow(faultType, faultDesc, degradedValues) {
        if (state.status !== 'healthy') return;

        state.status = 'degraded';
        state.activeChaos = faultType;
        Object.assign(state.metrics, degradedValues);
        state.metrics.mlScore = computeMLScore(degradedValues.latencyP95, degradedValues.errorRate, degradedValues.cpuUsage, degradedValues.memoryUsage);
        updateUI();

        addLog(`[CHAOS] Injected fault: ${faultDesc} into 'order-service'.`, 'danger');
        addLog(`[PROMETHEUS] Metric anomaly detected: Latency P95=${Math.round(degradedValues.latencyP95)}ms, ErrorRate=${degradedValues.errorRate.toFixed(1)}%.`, 'warning');

        // Step 1: ML Model Detection
        setTimeout(() => {
            addLog(`[ML-ALERT] Isolation Forest Anomaly Score: ${state.metrics.mlScore.toFixed(2)} (Threshold > 0.75 BREACHED).`, 'danger');
            addLog(`[ML-ENGINE] Anomaly signature: Multi-variate latency & error surge. Dispatching alert to Remediation Controller.`, 'warning');
        }, 1200);

        // Step 2: Remediation Policy & Guardrails
        setTimeout(() => {
            addLog(`[GUARDRAIL] Evaluating Remediation Policy Engine for target 'order-service'...`, 'info');
            addLog(`[GUARDRAIL] Allowlist Check: PASSED. Cooldown Timer (180s): PASSED. Rate Limit: OK.`, 'success');
            state.status = 'recovering';
            updateUI();
        }, 2400);

        // Step 3: Kubernetes Action Execution
        setTimeout(() => {
            addLog(`[K8S-ACTION] Executing kubectl rollout restart deployment/order-service in namespace 'cloudpulse'...`, 'cyan');
            state.metrics.restarts += 1;
            updateUI();
        }, 3600);

        // Step 4: System Recovery
        setTimeout(() => {
            addLog(`[K8S-POD] Fresh pod instance initialized and passed HTTP /health readiness probe.`, 'success');
            addLog(`[RECOVERY] Telemetry metrics normalized. MTTR: 2.14s. System restored to baseline.`, 'success');
            resetBaseline();
        }, 5200);
    }

    // Chaos Button Handlers
    document.getElementById('btn-chaos-kill').addEventListener('click', () => {
        triggerSelfHealingWorkflow('kill', 'Simulated sudden container OOM/SIGKILL crash', {
            latencyMean: 3500,
            latencyP95: 8400,
            errorRate: 64.5,
            requestRate: 88,
            cpuUsage: 450,
            memoryUsage: 250,
            restarts: state.metrics.restarts
        });
    });

    document.getElementById('btn-chaos-latency').addEventListener('click', () => {
        triggerSelfHealingWorkflow('latency', '5000ms Database Thread Pool Contention', {
            latencyMean: 2400,
            latencyP95: 5200,
            errorRate: 18.2,
            requestRate: 65,
            cpuUsage: 190,
            memoryUsage: 140,
            restarts: state.metrics.restarts
        });
    });

    document.getElementById('btn-chaos-errors').addEventListener('click', () => {
        triggerSelfHealingWorkflow('errors', '50% HTTP 500 Internal Server Error Cascade', {
            latencyMean: 850,
            latencyP95: 2100,
            errorRate: 50.0,
            requestRate: 72,
            cpuUsage: 160,
            memoryUsage: 110,
            restarts: state.metrics.restarts
        });
    });

    document.getElementById('btn-chaos-memory').addEventListener('click', () => {
        triggerSelfHealingWorkflow('memory', 'Memory Heap Saturation & Leak', {
            latencyMean: 1200,
            latencyP95: 3800,
            errorRate: 24.0,
            requestRate: 58,
            cpuUsage: 380,
            memoryUsage: 245,
            restarts: state.metrics.restarts
        });
    });

    // Run Full Simulation Button
    document.getElementById('btn-run-simulation').addEventListener('click', () => {
        addLog('[SIMULATION] Launching automated end-to-end self-healing demonstration cycle...', 'cyan');
        triggerSelfHealingWorkflow('full-cycle', 'E2E Automated Chaos & Self-Healing Cycle', {
            latencyMean: 4100,
            latencyP95: 9800,
            errorRate: 45.0,
            requestRate: 85,
            cpuUsage: 420,
            memoryUsage: 240,
            restarts: state.metrics.restarts
        });
    });

    // API Playground Interactive Handlers
    document.getElementById('btn-test-auth').addEventListener('click', () => {
        const dummyToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzcmVfb3BlcmF0b3IiLCJyb2xlIjoiYWRtaW4iLCJleHAiOjE4NTAwMDAwMDB9';
        addLog(`[API-AUTH] POST /api/v1/auth/login -> 200 OK (JWT Token generated)`, 'success');
        addLog(`[AUTH-TOKEN] ${dummyToken.substring(0, 36)}...`, 'info');
    });

    document.getElementById('btn-test-order').addEventListener('click', () => {
        const orderId = 'ord_' + Math.random().toString(36).substring(2, 9);
        addLog(`[API-ORDER] POST /api/v1/orders -> 201 Created (OrderID: ${orderId})`, 'success');
        addLog(`[RABBITMQ] Published event 'order-created' to exchange 'cloudpulse.events' -> Routing key: order.created`, 'cyan');
        setTimeout(() => {
            addLog(`[INVENTORY] Consumed event for Order ${orderId}: Reserved 2 units of SKU-CLOUD-99 in Inventory DB`, 'success');
        }, 500);
    });

    // Guided Tour Button
    document.getElementById('btn-guided-tour').addEventListener('click', () => {
        addLog('--- GUIDED TOUR: ARCHITECTURE & SELF-HEALING WALKTHROUGH ---', 'cyan');
        addLog('1. Microservices communicate via REST & RabbitMQ with Database-per-service isolation.', 'info');
        addLog('2. Prometheus scrapes latency, error rates, and resource utilization in real time.', 'info');
        addLog('3. Out-of-band Isolation Forest ML engine detects anomalous patterns with zero rule maintenance.', 'info');
        addLog('4. Remediation controller validates safety guardrails before recycling unhealthy pods via K8s API.', 'info');
        addLog('5. Try clicking "Kill Order Pod" or "Place Order" to interact with live simulations!', 'success');
    });

    // Interactive Node Click Handlers
    document.querySelectorAll('.service-node').forEach(node => {
        node.addEventListener('click', () => {
            const name = node.querySelector('.node-name')?.textContent || 'Node';
            const sub = node.querySelector('.node-sub')?.textContent || '';
            const db = node.querySelector('.node-db')?.textContent || '';
            addLog(`[INSPECT] Selected '${name}': ${sub} | Data Store: ${db} | Status: Healthy`, 'info');
        });
    });

    addLog('[READY] CloudPulse Command Center initialized and streaming live telemetry.', 'success');
});
