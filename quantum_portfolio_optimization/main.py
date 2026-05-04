import numpy as np
import pandas as pd
import json
import os
from data_collection import fetch_data
from preprocessing import calculate_returns_and_covariance
from classical_model import solve_classical_markowitz
from quantum_model import solve_quantum_qaoa
from utils import calculate_portfolio_performance
from visualization import plot_comprehensive_comparison

def main():
    print("=" * 50)
    print(" QUANTUM PORTFOLIO OPTIMIZATION USING QAOA ")
    print("=" * 50)
    
    # 1. Fetch Data
    tickers = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'AMZN']
    data = fetch_data(tickers)
    
    # 2. Preprocess Data
    expected_returns, cov_matrix = calculate_returns_and_covariance(data)
    
    # Parameter balancing return against risk (0.5 means equal concern)
    risk_factor = 0.5
    n_assets = len(tickers)
    total_subsets = 2 ** n_assets  # 2^5 = 32
    
    # 3. Classical Optimization
    print("\nRunning Classical Markowitz Optimization...")
    class_weights = solve_classical_markowitz(expected_returns, cov_matrix, risk_factor)
    class_perf = calculate_portfolio_performance(class_weights, expected_returns, cov_matrix)
    
    # 4. Quantum Optimization (QAOA)
    print("Running Quantum QAOA Optimization...")
    quant_binary = solve_quantum_qaoa(expected_returns, cov_matrix, risk_factor)
    
    # Decode Quantum Result: map binary {0, 1} to uniformly distributed weights
    selected_count = np.sum(quant_binary)
    if selected_count > 0:
        quant_weights = quant_binary / selected_count
    else:
        # fallback if QAOA selected nothing (rare edge case)
        quant_weights = np.ones(n_assets) / n_assets
        
    quant_perf = calculate_portfolio_performance(quant_weights, expected_returns, cov_matrix)
    
    # 5. Compute individual asset metrics for scatter plot
    company_perf = {}
    for i, ticker in enumerate(tickers):
        ret = float(expected_returns.iloc[i])
        risk = float(np.sqrt(cov_matrix.iloc[i, i]))
        company_perf[ticker] = (ret, risk)

    # 6. Build QAOA reasoning explanation
    selected_stocks = [t for t, b in zip(tickers, quant_binary) if b == 1.0]
    rejected_stocks = [t for t, b in zip(tickers, quant_binary) if b == 0.0]
    
    # Rank rejected stocks by their weakness
    rejection_reasons = {}
    for t in rejected_stocks:
        ret, rsk = company_perf[t]
        ratio = ret / rsk if rsk > 0 else 0
        # Determine the primary reason for rejection
        all_rets = [company_perf[s][0] for s in tickers]
        all_rsks = [company_perf[s][1] for s in tickers]
        if ret <= sorted(all_rets)[1]:  # bottom 2 returns
            rejection_reasons[t] = f"low return ({ret:+.1%})"
        elif rsk >= sorted(all_rsks)[-2]:  # top 2 risks
            rejection_reasons[t] = f"high risk ({rsk:.1%})"
        else:
            rejection_reasons[t] = f"poor return/risk ratio ({ratio:.2f})"
    
    qaoa_explanation = (
        f"QAOA evaluated all {total_subsets} possible stock subsets (2^{n_assets}), "
        f"analysed the risk-return tradeoff of each combination, "
        f"and concluded that {{{', '.join(selected_stocks)}}} is the optimal subset."
    )
    for t, reason in rejection_reasons.items():
        qaoa_explanation += f" {t} was excluded due to {reason}."

    # 7. Export results as JSON for the web frontend (before plt.show blocks)
    results = {
        "tickers": tickers,
        "classical": {
            "weights": [round(float(w), 4) for w in class_weights],
            "return": round(class_perf[0], 4),
            "risk": round(class_perf[1], 4),
            "sharpe": round(class_perf[2], 4)
        },
        "quantum": {
            "binary": [int(b) for b in quant_binary],
            "weights": [round(float(w), 4) for w in quant_weights],
            "return": round(quant_perf[0], 4),
            "risk": round(quant_perf[1], 4),
            "sharpe": round(quant_perf[2], 4),
            "selected": selected_stocks,
            "rejected": rejected_stocks,
            "rejectionReasons": rejection_reasons,
            "totalSubsets": total_subsets
        },
        "assets": {
            t: {"return": round(ret, 4), "risk": round(rsk, 4), "ratio": round(ret/rsk, 4) if rsk > 0 else 0}
            for t, (ret, rsk) in company_perf.items()
        },
        "qaoaExplanation": qaoa_explanation,
        "winner": "quantum" if quant_perf[2] > class_perf[2] else "classical" if class_perf[2] > quant_perf[2] else "tie"
    }
    
    frontend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'frontend')
    os.makedirs(frontend_dir, exist_ok=True)
    json_path = os.path.join(frontend_dir, 'data.json')
    with open(json_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"Results exported to {json_path}")
    
    # 8. Generate the full visual dashboard (plt.show() blocks until window closed)
    print("\nGenerating comprehensive dashboard...")
    plot_comprehensive_comparison(
        tickers, class_weights, quant_weights,
        class_perf, quant_perf, company_perf,
        qaoa_explanation, total_subsets
    )
    print("Done! Dashboard saved as portfolio_comprehensive_comparison.png")

if __name__ == "__main__":
    import warnings
    warnings.filterwarnings('ignore')  # Suppress Qiskit deprecation warnings for cleaner output
    main()
