import pandas as pd
import numpy as np

def calculate_returns_and_covariance(data):
    """
    Calculates the expected annual returns and the annual covariance matrix.
    Assuming 252 trading days in a year.
    """
    # Daily percentage returns
    daily_returns = data.pct_change().dropna()
    
    # Annualized Expected Returns
    expected_returns = daily_returns.mean() * 252
    
    # Annualized Covariance Matrix
    cov_matrix = daily_returns.cov() * 252
    
    return expected_returns, cov_matrix
