import sys, os
sys.path.insert(0, r'c:\Users\Shreyan\Quantum Portfolio Optimization using QAOA\quantum_portfolio_optimization')
os.chdir(r'c:\Users\Shreyan\Quantum Portfolio Optimization using QAOA\quantum_portfolio_optimization')
import warnings; warnings.filterwarnings('ignore')
import matplotlib; matplotlib.use('Agg')
import numpy as np, json
from data_collection import fetch_data
from preprocessing import calculate_returns_and_covariance
from classical_model import solve_classical_markowitz
from quantum_model import solve_quantum_qaoa
from utils import calculate_portfolio_performance

tickers = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'AMZN']
data = fetch_data(tickers)
expected_returns, cov_matrix = calculate_returns_and_covariance(data)
risk_factor = 0.5
n_assets = len(tickers)
total_subsets = 2 ** n_assets

class_weights = solve_classical_markowitz(expected_returns, cov_matrix, risk_factor)
class_perf = calculate_portfolio_performance(class_weights, expected_returns, cov_matrix)

quant_binary = solve_quantum_qaoa(expected_returns, cov_matrix, risk_factor)
selected_count = np.sum(quant_binary)
quant_weights = quant_binary / selected_count if selected_count > 0 else np.ones(n_assets) / n_assets
quant_perf = calculate_portfolio_performance(quant_weights, expected_returns, cov_matrix)

company_perf = {}
for i, t in enumerate(tickers):
    company_perf[t] = (float(expected_returns.iloc[i]), float(np.sqrt(cov_matrix.iloc[i, i])))

selected_stocks = [t for t, b in zip(tickers, quant_binary) if b == 1.0]
rejected_stocks = [t for t, b in zip(tickers, quant_binary) if b == 0.0]

rejection_reasons = {}
for t in rejected_stocks:
    ret, rsk = company_perf[t]
    all_rets = [company_perf[s][0] for s in tickers]
    all_rsks = [company_perf[s][1] for s in tickers]
    if ret <= sorted(all_rets)[1]:
        rejection_reasons[t] = "low return ({:+.1%})".format(ret)
    elif rsk >= sorted(all_rsks)[-2]:
        rejection_reasons[t] = "high risk ({:.1%})".format(rsk)
    else:
        rejection_reasons[t] = "poor return/risk ratio ({:.2f})".format(ret/rsk)

selected_str = ", ".join(selected_stocks)
qaoa_explanation = "QAOA evaluated all {} possible stock subsets (2^{}), analysed the risk-return tradeoff of each combination, and concluded that {{{}}} is the optimal subset.".format(total_subsets, n_assets, selected_str)
for t, reason in rejection_reasons.items():
    qaoa_explanation += " {} was excluded due to {}.".format(t, reason)

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

frontend_dir = r'c:\Users\Shreyan\Quantum Portfolio Optimization using QAOA\frontend'
os.makedirs(frontend_dir, exist_ok=True)
with open(os.path.join(frontend_dir, 'data.json'), 'w') as f:
    json.dump(results, f, indent=2)
print('data.json generated successfully!')
