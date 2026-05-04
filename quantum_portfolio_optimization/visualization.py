import matplotlib.pyplot as plt
import numpy as np
import textwrap

def plot_comprehensive_comparison(tickers, class_weights, quant_weights, class_perf, quant_perf, company_perf,
                                  qaoa_explanation="", total_subsets=32):
    """
    Plots a comprehensive dashboard with:
      - Top-left: Asset allocation bar chart (Classical vs Quantum)
      - Top-right: Risk vs Return scatter (individual stocks + both portfolios)
      - Bottom: Detailed data summary text panel with QAOA reasoning
    """
    fig = plt.figure(figsize=(18, 12))
    fig.patch.set_facecolor('#fafafa')
    
    # Create a grid: 2 columns on top, 1 spanning row on bottom for text
    gs = fig.add_gridspec(2, 2, height_ratios=[3, 2], hspace=0.35, wspace=0.3,
                          left=0.06, right=0.97, top=0.92, bottom=0.02)
    
    ax1 = fig.add_subplot(gs[0, 0])
    ax2 = fig.add_subplot(gs[0, 1])
    ax3 = fig.add_subplot(gs[1, :])  # spans both columns
    
    # ── Plot 1: Asset Allocation Bar Chart ──────────────────────────────
    x = np.arange(len(tickers))
    width = 0.32
    
    bars1 = ax1.bar(x - width/2, class_weights, width,
                    label='Classical (Bounded 5%–40%)', color='#3b82f6', edgecolor='white', linewidth=0.8)
    bars2 = ax1.bar(x + width/2, quant_weights, width,
                    label='Quantum QAOA (Binary QUBO)', color='#ef4444', edgecolor='white', linewidth=0.8)
    
    # Add percentage labels on top of each bar (including 0%)
    for bar, w in zip(bars1, class_weights):
        h = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2, max(h, 0) + 0.008, f'{w:.0%}',
                 ha='center', va='bottom', fontsize=8, fontweight='bold', color='#3b82f6')
    for bar, w in zip(bars2, quant_weights):
        h = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2, max(h, 0) + 0.008, f'{w:.0%}',
                 ha='center', va='bottom', fontsize=8, fontweight='bold', color='#ef4444')
    
    ax1.set_xlabel('Assets', fontsize=11)
    ax1.set_ylabel('Portfolio Weight', fontsize=11)
    ax1.set_title('Asset Allocation Comparison', fontsize=13, fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels(tickers, fontsize=10)
    ax1.set_ylim(0, max(max(class_weights), max(quant_weights)) * 1.3)
    ax1.legend(fontsize=9, loc='upper right')
    ax1.grid(True, linestyle='--', alpha=0.3, axis='y')
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    
    # ── Plot 2: Risk vs Return Scatter ──────────────────────────────────
    c_ret, c_risk, c_sharpe = class_perf
    q_ret, q_risk, q_sharpe = quant_perf
    
    # Individual stocks — plot with colored dots and clear labels
    stock_colors = ['#f59e0b', '#8b5cf6', '#10b981', '#ec4899', '#06b6d4']
    for idx, (tic, (ret, rsk)) in enumerate(company_perf.items()):
        col = stock_colors[idx % len(stock_colors)]
        ax2.scatter(rsk, ret, color=col, s=90, zorder=2, edgecolors='white', linewidth=0.8, alpha=0.85)
        ax2.annotate(tic, (rsk, ret), textcoords="offset points", xytext=(8, 4),
                     fontsize=9.5, fontweight='bold', color=col)

    # Portfolio dots — larger and prominent
    ax2.scatter(c_risk, c_ret, color='#3b82f6', s=300, zorder=4, edgecolors='white', linewidth=2,
                label=f'Classical  (Sharpe {c_sharpe:.2f})')
    ax2.scatter(q_risk, q_ret, color='#ef4444', s=380, marker='*', zorder=4, edgecolors='white', linewidth=1.2,
                label=f'Quantum   (Sharpe {q_sharpe:.2f})')
    
    ax2.annotate('Classical', (c_risk, c_ret), textcoords="offset points", xytext=(12, -10),
                 fontsize=10.5, fontweight='bold', color='#3b82f6')
    ax2.annotate('Quantum', (q_risk, q_ret), textcoords="offset points", xytext=(12, -10),
                 fontsize=10.5, fontweight='bold', color='#ef4444')

    ax2.set_title("Risk vs Expected Return", fontsize=13, fontweight='bold')
    ax2.set_xlabel("Risk (Annualised Volatility)", fontsize=11)
    ax2.set_ylabel("Expected Annual Return", fontsize=11)
    ax2.legend(fontsize=9, loc='lower right')
    ax2.grid(True, linestyle='--', alpha=0.3)
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    
    # Add some padding to axes so edge points aren't clipped
    all_risks = [rsk for _, (_, rsk) in company_perf.items()] + [c_risk, q_risk]
    all_rets  = [ret for _, (ret, _) in company_perf.items()] + [c_ret, q_ret]
    x_pad = (max(all_risks) - min(all_risks)) * 0.15
    y_pad = (max(all_rets) - min(all_rets)) * 0.15
    ax2.set_xlim(min(all_risks) - x_pad, max(all_risks) + x_pad)
    ax2.set_ylim(min(all_rets) - y_pad, max(all_rets) + y_pad)
    
    # ── Plot 3: Data Summary Panel ──────────────────────────────────────
    ax3.axis('off')
    
    divider = "─" * 85
    
    # Build individual asset lines (two rows to avoid overflow)
    asset_items = [f"{tic}: Ret {ret:+.2%}, Risk {rsk:.2%}" for tic, (ret, rsk) in company_perf.items()]
    row1 = "   ".join(asset_items[:3])
    row2 = "   ".join(asset_items[3:]) if len(asset_items) > 3 else ""
    
    # Classical vs Quantum
    cw_str = ", ".join([f"{t}:{w:.0%}" for t, w in zip(tickers, class_weights)])
    qw_str = ", ".join([f"{t}:{w:.0%}" for t, w in zip(tickers, quant_weights)])
    
    classical_line = f"CLASSICAL  │  {cw_str}  │  Return: {c_ret:.4f}  │  Risk: {c_risk:.4f}  │  Sharpe: {c_sharpe:.4f}"
    quantum_line   = f"QUANTUM    │  {qw_str}  │  Return: {q_ret:.4f}  │  Risk: {q_risk:.4f}  │  Sharpe: {q_sharpe:.4f}"
    
    # Winner
    if c_sharpe > q_sharpe:
        winner = "Classical Optimization"
    elif q_sharpe > c_sharpe:
        winner = "Quantum QAOA"
    else:
        winner = "Tie"
    
    verdict = f"WINNER: {winner}  (Higher Sharpe Ratio = Better Risk-Adjusted Return)"
    
    # Wrap the QAOA explanation to fit nicely
    wrapped_explanation = "\n".join(textwrap.wrap(qaoa_explanation, width=95))
    
    full_text = (
        f"DETAILED PERFORMANCE SUMMARY\n"
        f"{divider}\n"
        f"INDIVIDUAL ASSETS:\n"
        f"  {row1}\n"
    )
    if row2:
        full_text += f"  {row2}\n"
    full_text += (
        f"{divider}\n"
        f"{classical_line}\n"
        f"{quantum_line}\n"
        f"{divider}\n"
        f"{verdict}\n"
        f"{divider}\n"
        f"QAOA REASONING:\n"
        f"{wrapped_explanation}\n\n"
        f"Note: QAOA uses QUBO (binary 0/1 selection). Selected assets receive equal weight.\n"
        f"Classical model is bounded [5%–40%] per asset to enforce diversification."
    )
    
    ax3.text(0.5, 0.5, full_text, transform=ax3.transAxes,
             ha='center', va='center', fontsize=9, family='monospace',
             bbox=dict(facecolor='white', edgecolor='#d1d5db', boxstyle='round,pad=0.8', linewidth=1.2))
    
    fig.suptitle("Quantum Portfolio Optimization using QAOA", fontsize=16, fontweight='bold', y=0.97)
    plt.savefig("portfolio_comprehensive_comparison.png", dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.show()
