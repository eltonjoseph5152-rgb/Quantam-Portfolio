import numpy as np

def calculate_portfolio_performance(weights, expected_returns, cov_matrix):
    """
    Calculates expected return, risk (volatility), and Sharpe ratio.
    Safely converts pandas objects to numpy arrays before computation.
    """
    w = np.array(weights, dtype=float)
    mu = np.array(expected_returns, dtype=float)
    sigma = np.array(cov_matrix, dtype=float)
    
    # Expected Annual Return: w^T * mu
    port_return = np.dot(w, mu)
    
    # Expected Risk (Volatility): sqrt(w^T * Sigma * w)
    port_risk = np.sqrt(np.dot(w.T, np.dot(sigma, w)))
    
    # Sharpe Ratio (Assuming Risk-Free Rate = 0 for simplicity)
    sharpe_ratio = port_return / port_risk if port_risk > 0 else 0.0
    
    return float(port_return), float(port_risk), float(sharpe_ratio)
