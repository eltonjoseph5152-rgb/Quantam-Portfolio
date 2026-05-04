import numpy as np
from qiskit_optimization import QuadraticProgram
from qiskit_optimization.algorithms import MinimumEigenOptimizer
from qiskit_algorithms import QAOA
from qiskit_algorithms.optimizers import COBYLA
from qiskit.primitives import StatevectorSampler as Sampler

def solve_quantum_qaoa(expected_returns, cov_matrix, risk_factor=0.5):
    """
    Formulates a Quadratic Unconstrained Binary Optimization (QUBO) model 
    for the portfolio and solves it using QAOA.
    
    Binary variable q_i = 1 means we invest in asset i, q_i = 0 means we do not.
    
    Objective: minimize  risk_factor * (q^T * Cov * q) - (1 - risk_factor) * (mu^T * q)
    """
    # Force explicit conversion to float64 numpy arrays to prevent Qiskit complex parsing bugs
    exp_ret = np.array(expected_returns, dtype=np.float64)
    cov_mat = np.array(cov_matrix, dtype=np.float64)
    
    n_assets = len(exp_ret)
    qp = QuadraticProgram()
    
    # Define binary variables for each asset
    for i in range(n_assets):
        qp.binary_var(name=f"x_{i}")
        
    linear_terms = {}
    quadratic_terms = {}
    
    for i in range(n_assets):
        # Linear part: -(1 - risk_factor) * expected_returns[i]
        linear_terms[f"x_{i}"] = float(-(1 - risk_factor) * exp_ret[i])
        for j in range(i, n_assets):
            # Quadratic part: risk_factor * cov_matrix[i,j]
            # Only upper triangle needed — qiskit handles symmetry
            key = (f"x_{i}", f"x_{j}")
            val = float(risk_factor * cov_mat[i, j])
            if i == j:
                quadratic_terms[key] = val
            else:
                # Off-diagonal: pass full (i,j) value; qiskit splits symmetry internally
                quadratic_terms[key] = 2.0 * val
            
    qp.minimize(linear=linear_terms, quadratic=quadratic_terms)

    # Setup QAOA with p=1 (reps=1): a single layer of the QAOA ansatz.
    # Higher reps can improve quality but increase circuit depth and runtime.
    sampler = Sampler() 
    optimizer = COBYLA(maxiter=100)
    qaoa = QAOA(sampler=sampler, optimizer=optimizer, reps=1)
    
    # Map the problem to QAOA using MinimumEigenOptimizer
    optimizer_algo = MinimumEigenOptimizer(qaoa)
    
    print("Solving QUBO with QAOA...")
    result = optimizer_algo.solve(qp)
    print("QAOA Optimization complete.")
    
    # Return binary solution as a numpy array
    return np.array(result.x, dtype=float)
