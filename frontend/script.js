// ── Data ───────────────────────────────────────────────────────
// Pre-computed results from the Python QAOA pipeline.
// To regenerate: run `python main.py` which writes frontend/data.json
let DATA = null;

const STOCK_COLORS = {
    'AAPL': '#f59e0b',
    'MSFT': '#8b5cf6',
    'GOOGL': '#10b981',
    'TSLA': '#ec4899',
    'AMZN': '#06b6d4'
};

// ── Load Data ──────────────────────────────────────────────────
async function loadData() {
    try {
        const resp = await fetch('./data.json');
        DATA = await resp.json();
    } catch {
        // Fallback: use embedded sample data if data.json not available
        DATA = {
            tickers: ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'AMZN'],
            classical: { weights: [0.05, 0.4, 0.4, 0.05, 0.1], return: 0.5435, risk: 0.2316, sharpe: 2.3473 },
            quantum: {
                binary: [1, 1, 1, 0, 0],
                weights: [0.3333, 0.3333, 0.3333, 0, 0],
                return: 0.4997, risk: 0.2092, sharpe: 2.3882,
                selected: ['AAPL', 'MSFT', 'GOOGL'],
                rejected: ['TSLA', 'AMZN'],
                rejectionReasons: { TSLA: 'low return (+12.1%)', AMZN: 'high risk (47.5%)' },
                totalSubsets: 32
            },
            assets: {
                AAPL: { return: 0.2895, risk: 0.2348, ratio: 1.2330 },
                MSFT: { return: 0.3929, risk: 0.3094, ratio: 1.2699 },
                GOOGL: { return: 0.8168, risk: 0.2848, ratio: 2.8680 },
                TSLA: { return: 0.1211, risk: 0.2456, ratio: 0.4932 },
                AMZN: { return: 0.3913, risk: 0.4748, ratio: 0.8241 }
            },
            qaoaExplanation: "QAOA evaluated all 32 possible stock subsets (2^5), analysed the risk-return tradeoff of each combination, and concluded that {AAPL, MSFT, GOOGL} is the optimal subset. TSLA was excluded due to low return (+12.1%). AMZN was excluded due to high risk (47.5%).",
            winner: 'quantum'
        };
    }
    render();
}

// ── Render Everything ──────────────────────────────────────────
function render() {
    renderHeroStats();
    renderQAOAExplanation();
    renderAllocationChart();
    renderRiskReturnChart();
    renderAssetCards();
    renderComparisonTable();
    renderWinner();
    setupScrollAnimations();
}

// ── Hero Stats ─────────────────────────────────────────────────
function renderHeroStats() {
    const el = document.getElementById('hero-stats');
    const stats = [
        { value: DATA.tickers.length, label: 'Assets Analysed' },
        { value: DATA.quantum.totalSubsets, label: 'Subsets Evaluated' },
        { value: DATA.quantum.selected.length, label: 'QAOA Selected' },
        { value: DATA.winner === 'quantum' ? 'QAOA' : 'Classical', label: 'Winner' }
    ];
    el.innerHTML = stats.map(s => `
        <div class="hero-stat">
            <span class="hero-stat-value">${s.value}</span>
            <span class="hero-stat-label">${s.label}</span>
        </div>
    `).join('');
}

// ── QAOA Explanation ───────────────────────────────────────────
function renderQAOAExplanation() {
    document.getElementById('qaoa-explanation-text').textContent = DATA.qaoaExplanation;

    const grid = document.getElementById('explanation-grid');
    grid.innerHTML = DATA.tickers.map(ticker => {
        const asset = DATA.assets[ticker];
        const isSelected = DATA.quantum.selected.includes(ticker);
        const reason = DATA.quantum.rejectionReasons[ticker];
        const statusClass = isSelected ? 'selected' : 'rejected';
        const badgeClass = isSelected ? 'badge-selected' : 'badge-rejected';
        const badgeText = isSelected ? '✓ Selected' : '✗ Rejected';
        const color = STOCK_COLORS[ticker] || '#888';

        let reasonText = '';
        if (isSelected) {
            reasonText = `Strong return-to-risk ratio of ${asset.ratio.toFixed(2)}. QAOA determined this asset improves the portfolio's overall risk-adjusted performance.`;
        } else {
            reasonText = `Excluded: ${reason}. Return/Risk ratio of only ${asset.ratio.toFixed(2)} — adding this asset would worsen the portfolio's Sharpe Ratio.`;
        }

        return `
            <div class="explanation-card ${statusClass}">
                <div class="explanation-card-header">
                    <span class="explanation-card-ticker" style="color: ${color}">${ticker}</span>
                    <span class="explanation-card-badge ${badgeClass}">${badgeText}</span>
                </div>
                <div class="explanation-card-metrics">
                    <div class="metric">
                        <div class="metric-label">Annual Return</div>
                        <div class="metric-value" style="color: ${asset.return >= 0 ? '#22c55e' : '#ef4444'}">${(asset.return * 100).toFixed(1)}%</div>
                    </div>
                    <div class="metric">
                        <div class="metric-label">Risk (Volatility)</div>
                        <div class="metric-value">${(asset.risk * 100).toFixed(1)}%</div>
                    </div>
                </div>
                <div class="explanation-card-reason">${reasonText}</div>
            </div>
        `;
    }).join('');
}

// ── Allocation Bar Chart ───────────────────────────────────────
function renderAllocationChart() {
    const ctx = document.getElementById('allocationChart').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: DATA.tickers,
            datasets: [
                {
                    label: 'Classical (5%–40%)',
                    data: DATA.classical.weights.map(w => w * 100),
                    backgroundColor: 'rgba(59, 130, 246, 0.7)',
                    borderColor: '#3b82f6',
                    borderWidth: 1,
                    borderRadius: 6,
                    barPercentage: 0.7,
                    categoryPercentage: 0.65
                },
                {
                    label: 'Quantum QAOA',
                    data: DATA.quantum.weights.map(w => w * 100),
                    backgroundColor: 'rgba(239, 68, 68, 0.7)',
                    borderColor: '#ef4444',
                    borderWidth: 1,
                    borderRadius: 6,
                    barPercentage: 0.7,
                    categoryPercentage: 0.65
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: { duration: 1200, easing: 'easeOutQuart' },
            plugins: {
                legend: {
                    labels: { color: '#a1a1aa', font: { family: "'Inter'", size: 12 }, usePointStyle: true, padding: 20 }
                },
                tooltip: {
                    backgroundColor: 'rgba(15,15,25,0.95)',
                    borderColor: 'rgba(255,255,255,0.1)',
                    borderWidth: 1,
                    titleFont: { family: "'Inter'", weight: '600' },
                    bodyFont: { family: "'JetBrains Mono'", size: 13 },
                    callbacks: { label: ctx => `${ctx.dataset.label}: ${ctx.parsed.y.toFixed(1)}%` }
                }
            },
            scales: {
                x: {
                    ticks: { color: '#71717a', font: { family: "'Inter'", size: 13, weight: '600' } },
                    grid: { display: false }
                },
                y: {
                    ticks: { color: '#71717a', font: { family: "'JetBrains Mono'", size: 11 }, callback: v => v + '%' },
                    grid: { color: 'rgba(255,255,255,0.04)' },
                    beginAtZero: true
                }
            }
        }
    });
}

// ── Risk vs Return Scatter ─────────────────────────────────────
function renderRiskReturnChart() {
    const ctx = document.getElementById('riskReturnChart').getContext('2d');

    // Individual stock data points
    const stockPoints = DATA.tickers.map(t => ({
        x: DATA.assets[t].risk * 100,
        y: DATA.assets[t].return * 100,
        label: t
    }));

    new Chart(ctx, {
        type: 'scatter',
        data: {
            datasets: [
                // Individual stocks
                ...DATA.tickers.map((t, i) => ({
                    label: t,
                    data: [{ x: DATA.assets[t].risk * 100, y: DATA.assets[t].return * 100 }],
                    backgroundColor: STOCK_COLORS[t],
                    borderColor: STOCK_COLORS[t],
                    pointRadius: 8,
                    pointHoverRadius: 12,
                    pointStyle: 'circle'
                })),
                // Classical portfolio
                {
                    label: `Classical (Sharpe ${DATA.classical.sharpe.toFixed(2)})`,
                    data: [{ x: DATA.classical.risk * 100, y: DATA.classical.return * 100 }],
                    backgroundColor: '#3b82f6',
                    borderColor: '#fff',
                    borderWidth: 2,
                    pointRadius: 14,
                    pointHoverRadius: 18,
                    pointStyle: 'circle'
                },
                // Quantum portfolio
                {
                    label: `Quantum (Sharpe ${DATA.quantum.sharpe.toFixed(2)})`,
                    data: [{ x: DATA.quantum.risk * 100, y: DATA.quantum.return * 100 }],
                    backgroundColor: '#ef4444',
                    borderColor: '#fff',
                    borderWidth: 2,
                    pointRadius: 16,
                    pointHoverRadius: 20,
                    pointStyle: 'star'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: { duration: 1400, easing: 'easeOutQuart' },
            plugins: {
                legend: {
                    labels: {
                        color: '#a1a1aa',
                        font: { family: "'Inter'", size: 11 },
                        usePointStyle: true,
                        padding: 14
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(15,15,25,0.95)',
                    borderColor: 'rgba(255,255,255,0.1)',
                    borderWidth: 1,
                    titleFont: { family: "'Inter'", weight: '600' },
                    bodyFont: { family: "'JetBrains Mono'", size: 13 },
                    callbacks: {
                        label: ctx => `${ctx.dataset.label}: Risk ${ctx.parsed.x.toFixed(1)}%, Return ${ctx.parsed.y.toFixed(1)}%`
                    }
                }
            },
            scales: {
                x: {
                    title: { display: true, text: 'Risk (Annualised Volatility %)', color: '#71717a', font: { family: "'Inter'", size: 12 } },
                    ticks: { color: '#71717a', font: { family: "'JetBrains Mono'", size: 11 }, callback: v => v + '%' },
                    grid: { color: 'rgba(255,255,255,0.04)' }
                },
                y: {
                    title: { display: true, text: 'Expected Annual Return %', color: '#71717a', font: { family: "'Inter'", size: 12 } },
                    ticks: { color: '#71717a', font: { family: "'JetBrains Mono'", size: 11 }, callback: v => v + '%' },
                    grid: { color: 'rgba(255,255,255,0.04)' }
                }
            }
        }
    });
}

// ── Asset Cards ────────────────────────────────────────────────
function renderAssetCards() {
    const el = document.getElementById('asset-cards');
    const maxReturn = Math.max(...Object.values(DATA.assets).map(a => Math.abs(a.return)));

    el.innerHTML = DATA.tickers.map((t, i) => {
        const a = DATA.assets[t];
        const color = STOCK_COLORS[t];
        const barWidth = (Math.abs(a.return) / maxReturn * 100).toFixed(0);
        const isSelected = DATA.quantum.selected.includes(t);

        return `
            <div class="asset-card" style="animation-delay: ${i * 0.1}s; border-top: 3px solid ${color}">
                <div class="asset-card-ticker" style="color: ${color}">${t}</div>
                <div class="asset-card-metric">
                    <div class="asset-card-metric-label">Annual Return</div>
                    <div class="asset-card-metric-value" style="color: ${a.return >= 0 ? '#22c55e' : '#ef4444'}">
                        ${a.return >= 0 ? '+' : ''}${(a.return * 100).toFixed(1)}%
                    </div>
                </div>
                <div class="asset-card-metric">
                    <div class="asset-card-metric-label">Risk</div>
                    <div class="asset-card-metric-value">${(a.risk * 100).toFixed(1)}%</div>
                </div>
                <div class="asset-card-metric">
                    <div class="asset-card-metric-label">Return / Risk</div>
                    <div class="asset-card-metric-value">${a.ratio.toFixed(2)}</div>
                </div>
                <div class="asset-card-metric">
                    <div class="asset-card-metric-label">QAOA Decision</div>
                    <div class="asset-card-metric-value" style="color: ${isSelected ? '#22c55e' : '#ef4444'}; font-size: 14px;">
                        ${isSelected ? '✓ Invest' : '✗ Skip'}
                    </div>
                </div>
                <div class="asset-card-bar">
                    <div class="asset-card-bar-fill" style="width: ${barWidth}%; background: ${color}"></div>
                </div>
            </div>
        `;
    }).join('');
}

// ── Comparison Table ───────────────────────────────────────────
function renderComparisonTable() {
    const el = document.getElementById('comparison-table');
    const c = DATA.classical;
    const q = DATA.quantum;

    const rows = [
        ['Approach', 'Continuous (SLSQP)', 'Binary QUBO (QAOA)'],
        ['Weights', c.weights.map((w, i) => `${DATA.tickers[i]}:${(w*100).toFixed(0)}%`).join(', '),
                    q.weights.map((w, i) => `${DATA.tickers[i]}:${(w*100).toFixed(0)}%`).join(', ')],
        ['Expected Return', (c.return * 100).toFixed(2) + '%', (q.return * 100).toFixed(2) + '%'],
        ['Portfolio Risk', (c.risk * 100).toFixed(2) + '%', (q.risk * 100).toFixed(2) + '%'],
        ['Sharpe Ratio', c.sharpe.toFixed(4), q.sharpe.toFixed(4)],
        ['Diversification', 'Bounded 5%–40%', 'Equal split among selected'],
        ['Subsets Checked', 'N/A (continuous)', `All ${q.totalSubsets} combinations`]
    ];

    // Determine which sharpe is higher
    const classicalWins = c.sharpe > q.sharpe;

    el.innerHTML = `
        <thead>
            <tr>
                <th>Metric</th>
                <th style="color: ${classicalWins ? '#3b82f6' : '#a1a1aa'}">Classical ${classicalWins ? '👑' : ''}</th>
                <th style="color: ${!classicalWins ? '#ef4444' : '#a1a1aa'}">Quantum ${!classicalWins ? '👑' : ''}</th>
            </tr>
        </thead>
        <tbody>
            ${rows.map(([label, cv, qv]) => `
                <tr>
                    <td class="table-label">${label}</td>
                    <td>${cv}</td>
                    <td>${qv}</td>
                </tr>
            `).join('')}
        </tbody>
    `;
}

// ── Winner ─────────────────────────────────────────────────────
function renderWinner() {
    const el = document.getElementById('winner-card');
    const isQuantum = DATA.winner === 'quantum';
    const winnerName = isQuantum ? 'Quantum QAOA' : 'Classical Markowitz';
    const winnerSharpe = isQuantum ? DATA.quantum.sharpe : DATA.classical.sharpe;
    const loserSharpe = isQuantum ? DATA.classical.sharpe : DATA.quantum.sharpe;
    const emoji = isQuantum ? '⚛️' : '📐';

    el.innerHTML = `
        <div class="winner-card-inner">
            <div class="winner-emoji">${emoji}</div>
            <div class="winner-label">Superior Risk-Adjusted Performance</div>
            <div class="winner-name gradient-text">${winnerName}</div>
            <div class="winner-sharpe">
                Sharpe Ratio: <strong>${winnerSharpe.toFixed(4)}</strong>
                <span style="color: var(--text-muted); margin-left: 12px;">vs ${loserSharpe.toFixed(4)}</span>
            </div>
        </div>
    `;
}

// ── Scroll Animations ──────────────────────────────────────────
function setupScrollAnimations() {
    const observer = new IntersectionObserver(
        entries => entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        }),
        { threshold: 0.1 }
    );

    document.querySelectorAll('.section, .chart-card, .tech-card, .asset-card, .explanation-card').forEach(el => {
        el.classList.add('animate-in');
        observer.observe(el);
    });
}

// ── Init ───────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', loadData);
