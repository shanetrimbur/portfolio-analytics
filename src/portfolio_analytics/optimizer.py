import numpy as np
from scipy.optimize import minimize
from typing import Tuple, Dict, Optional
import pandas as pd

class PortfolioOptimizer:
    """
    A sophisticated portfolio optimization engine implementing Modern Portfolio Theory (MPT)
    with support for various optimization objectives and constraints.
    """
    
    def __init__(self, returns_data: pd.DataFrame):
        """
        Initialize the optimizer with historical returns data.
        
        Args:
            returns_data (pd.DataFrame): Historical returns for multiple assets
        """
        self.returns = returns_data
        self.mean_returns = self.returns.mean() * 252  # Annualized returns
        self.cov_matrix = self.returns.cov() * 252    # Annualized covariance
        
    def optimize_sharpe_ratio(
        self, 
        risk_free_rate: float = 0.02,
        constraints: Optional[Dict] = None
    ) -> Tuple[np.ndarray, float]:
        """
        Optimize portfolio weights to maximize the Sharpe Ratio.
        
        Args:
            risk_free_rate (float): Annual risk-free rate
            constraints (Dict): Additional optimization constraints
            
        Returns:
            Tuple[np.ndarray, float]: Optimal weights and corresponding Sharpe ratio
        """
        num_assets = len(self.returns.columns)
        constraints = constraints or []
        
        # Base constraints
        constraints = [
            {'type': 'eq', 'fun': lambda x: np.sum(x) - 1},  # Weights sum to 1
            {'type': 'ineq', 'fun': lambda x: x}             # Long-only constraint
        ] + constraints
        
        def negative_sharpe_ratio(weights: np.ndarray) -> float:
            portfolio_return = np.sum(self.mean_returns * weights)
            portfolio_std = np.sqrt(np.dot(weights.T, np.dot(self.cov_matrix, weights)))
            sharpe = (portfolio_return - risk_free_rate) / portfolio_std
            return -sharpe
        
        result = minimize(
            negative_sharpe_ratio,
            x0=np.array([1/num_assets] * num_assets),
            method='SLSQP',
            constraints=constraints,
            tol=1e-10
        )
        
        optimal_sharpe = -negative_sharpe_ratio(result.x)
        return result.x, optimal_sharpe
    
    def efficient_frontier(
        self, 
        num_portfolios: int = 100
    ) -> pd.DataFrame:
        """
        Generate the efficient frontier by calculating optimal portfolios
        for different target returns.
        
        Args:
            num_portfolios (int): Number of portfolios to generate
            
        Returns:
            pd.DataFrame: Portfolio weights and metrics along the efficient frontier
        """
        min_ret = np.min(self.mean_returns)
        max_ret = np.max(self.mean_returns)
        target_returns = np.linspace(min_ret, max_ret, num_portfolios)
        
        results = []
        for target_return in target_returns:
            constraints = [
                {'type': 'eq', 'fun': lambda x: np.sum(x) - 1},
                {'type': 'eq', 'fun': lambda x: np.sum(self.mean_returns * x) - target_return},
                {'type': 'ineq', 'fun': lambda x: x}
            ]
            
            result = minimize(
                lambda x: np.sqrt(np.dot(x.T, np.dot(self.cov_matrix, x))),
                x0=np.array([1/len(self.returns.columns)] * len(self.returns.columns)),
                method='SLSQP',
                constraints=constraints
            )
            
            std = np.sqrt(np.dot(result.x.T, np.dot(self.cov_matrix, result.x)))
            results.append({
                'return': target_return,
                'volatility': std,
                'weights': result.x
            })
            
        return pd.DataFrame(results)

    def calculate_metrics(self, weights: np.ndarray) -> Dict[str, float]:
        """
        Calculate key portfolio metrics for given weights.
        
        Args:
            weights (np.ndarray): Portfolio weights
            
        Returns:
            Dict[str, float]: Dictionary of portfolio metrics
        """
        portfolio_return = np.sum(self.mean_returns * weights)
        portfolio_std = np.sqrt(np.dot(weights.T, np.dot(self.cov_matrix, weights)))
        
        metrics = {
            'expected_return': portfolio_return,
            'volatility': portfolio_std,
            'sharpe_ratio': (portfolio_return - 0.02) / portfolio_std  # Assuming 2% risk-free rate
        }
        
        return metrics