import numpy as np
from scipy.optimize import minimize

def solve_classical_markowitz(expected_returns, cov_matrix, risk_factor=0.5):
    """
    Solves the classical Markowitz Mean-Variance optimization.
    Minimizes: risk_factor * (w^T * Cov * w) - (1 - risk_factor) * (w^T * expected_returns)
    Constraints: sum(weights) = 1, each weight bounded [5%, 40%] for diversification.
    """
    # Ensure they are float numpy arrays
    exp_ret = np.array(expected_returns, dtype=float)
    cov_mat = np.array(cov_matrix, dtype=float)
    
    n_assets = len(exp_ret)
    
    def objective_function(weights):
        port_variance = np.dot(weights.T, np.dot(cov_mat, weights))
        port_return = np.dot(exp_ret, weights)
        return risk_factor * port_variance - (1 - risk_factor) * port_return
        
    # Constraints as a list (correct scipy convention)
    constraints = [{'type': 'eq', 'fun': lambda x: np.sum(x) - 1.0}]
    
    # Strict diversification criteria for Classical Model
    # Ensures no asset is completely ignored (min 5%) and no asset dominates over 40%
    bounds = tuple((0.05, 0.40) for _ in range(n_assets))
    
    # Start with equal allocation
    init_guess = np.full(n_assets, 1.0 / n_assets)
    
    result = minimize(
        objective_function, 
        init_guess, 
        method='SLSQP', 
        bounds=bounds, 
        constraints=constraints
    )
    
    if not result.success:
        print(f"[WARNING] Classical optimizer did not converge: {result.message}")
    
    return result.x
