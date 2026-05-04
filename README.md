# Quantum Portfolio Optimization Using QAOA

Welcome to the **Quantum Portfolio Optimization** project. This project leverages both classical optimization algorithms and quantum computing approaches (specifically the Quantum Approximate Optimization Algorithm - QAOA) to find optimal asset allocations in a stock portfolio. It features a complete pipeline from a Python-based backend simulation to an elegant interactive frontend dashboard.

## Overview

Modern portfolio theory seeks to maximize return for a given level of risk. This project contrasts two distinct approaches:
1. **Classical Markowitz Mean-Variance Optimization:** Uses continuous weights and a classical solver (SLSQP via `scipy.optimize`) to balance portfolio diversification, enforcing practical weight bounds on each asset.
2. **Quantum Optimization (QAOA):** Reformulates the portfolio selection into a Quadratic Unconstrained Binary Optimization (QUBO) problem. Utilizing Qiskit's QAOA ansatz and COBYLA optimizer, it explores a combinatorial approach (buy/don't buy) suited for quantum hardware, evaluating the assets using a local simulator (`StatevectorSampler`).

The backend outputs the results as JSON, which are then consumed by a sleek, modern frontend dashboard that visualizes the metrics and allocations dynamically.

## Project Structure

The repository is structured into two main components:

### 1. `quantum_portfolio_optimization/` (Backend / Core Logic)
This directory contains the core quantum and classical simulation models.
- **`data_collection.py`**: Fetches 1 year of real-world stock data using `yfinance`.
- **`preprocessing.py`**: Computes annualized returns and the covariance matrix.
- **`classical_model.py`**: Implements Markowitz Mean-Variance optimization.
- **`quantum_model.py`**: Formulates QUBO and solves using Qiskit's QAOA.
- **`utils.py` / `visualization.py`**: Calculates portfolio performance metrics and generates matplotlib comparisons.
- **`main.py` / `export_json.py`**: Orchestrates the pipeline and exports results to be consumed by the frontend.
- **`requirements.txt`**: Backend Python dependencies.

### 2. `frontend/` (Interactive Dashboard)
A sophisticated vanilla HTML/CSS/JS frontend to visualize the portfolio optimization results.
- **`index.html`**: The structure of the dashboard.
- **`style.css`**: Premium styling, responsive design, animations, and glassmorphism UI elements.
- **`script.js`**: Fetches the JSON output (`data.json`) from the backend, parsing and rendering interactive charts and metric cards.

## Setup & Installation

### Backend Setup
We recommend using Python 3.9+ and a virtual environment.

```bash
cd quantum_portfolio_optimization
python -m venv .venv

# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
```

Run the main pipeline to fetch data and run the quantum and classical optimizers:
```bash
python main.py
```
This generates the comprehensive matplotlib charts and the necessary data for the frontend.

### Frontend Setup
No build tools are required. Simply serve the `frontend/` directory using any local web server to view the dashboard:

```bash
cd frontend
# Using Python's built-in HTTP server:
python -m http.server 8000
```
Then, open `http://localhost:8000` in your web browser.

## Limitations & Future Work

- **Simulation Limitations:** Currently utilizes Qiskit's `StatevectorSampler` (exact simulator). Executing on real quantum hardware would introduce noise and device queuing.
- **Asset Universe:** Currently restricted to a small asset universe to ensure rapid quantum simulation completion.
- **Binary Simplification:** The QAOA approach simplifies portfolio allocation to a binary selection (select/don't select) with equally distributed weights among chosen assets, serving as a conceptual demonstration of QUBO applicability.
