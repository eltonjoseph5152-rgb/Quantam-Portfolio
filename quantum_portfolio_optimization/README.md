# Quantum Portfolio Optimization using QAOA

## Overview
This project compares **classical portfolio optimization** (Markowitz Mean-Variance) with a **quantum approach** using the **Quantum Approximate Optimization Algorithm (QAOA)**. It fetches real-world stock data, runs both optimizers, and produces a comprehensive visual dashboard.

## Classical vs Quantum Approach

### Classical Markowitz Optimization
- **Goal:** Find continuous weight percentages for each asset (e.g., 20% AAPL, 30% MSFT).
- **Constraints:** Weights sum to 100%. Diversification is enforced: each asset is bounded between 5% and 40%.
- **Solver:** `scipy.optimize.minimize` with the SLSQP method.

### Quantum Optimization (QAOA)
- **Goal:** Reformulate portfolio selection as a **Quadratic Unconstrained Binary Optimization (QUBO)** — a combinatorial problem well-suited to quantum hardware.
- **Variables:** Binary (0 or 1) per asset — either invest or don't. Selected assets share weight equally.
- **Solver:** Qiskit's `QAOA` ansatz (depth p=1) with `COBYLA` optimizer, executed on a local `StatevectorSampler` simulator.

## Project Structure
```
quantum_portfolio_optimization/
├── data_collection.py    # Fetches 1 year of stock data via yfinance
├── preprocessing.py      # Computes annualised returns & covariance matrix
├── classical_model.py    # Markowitz Mean-Variance optimizer (scipy)
├── quantum_model.py      # QUBO formulation + QAOA solver (Qiskit)
├── utils.py              # Portfolio performance metrics (return, risk, Sharpe)
├── visualization.py      # Comprehensive matplotlib dashboard
├── main.py               # Orchestrator — runs the full pipeline
├── requirements.txt      # Python dependencies
└── README.md
```

## Prerequisites
Python 3.9+ recommended. Install dependencies in a virtual environment:
```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
```

## How to Run
```bash
python main.py
```

## Output
- A matplotlib window with a **3-panel dashboard**:
  - **Top-left:** Asset allocation bar chart comparing Classical vs Quantum weights.
  - **Top-right:** Risk vs Return scatter plot showing individual stocks and both portfolio solutions.
  - **Bottom panel:** Detailed performance data, weights, and the winner verdict.
- The dashboard is also saved as `portfolio_comprehensive_comparison.png`.

## Limitations
- **Simulated Hardware:** Uses Qiskit's `StatevectorSampler` (exact simulator). Real quantum hardware would introduce noise and queue times.
- **Small Universe:** Limited to 5 assets so the quantum simulation completes rapidly. Real portfolios scan thousands.
- **Binary Simplification:** QUBO selects assets (buy/don't buy) but doesn't optimise continuous weights. Selected assets get equal weight.
