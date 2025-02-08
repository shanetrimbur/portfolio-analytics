import numpy as np
import pandas as pd
from typing import Dict, Optional

class RiskAnalyzer:
    """
    Comprehensive risk analysis toolkit for portfolio management.
    Implements various risk metrics and scenario analysis tools.
    """
    
    def __init__(self, returns_data: pd.DataFrame, weights: np.ndarray):
        """
        Initialize risk analyzer with portfolio data.
        
        Args:
            returns_data (pd.DataFrame): Historical returns for assets
            weights (np.ndarray): Portfolio weights
        """
        self.returns = returns_data
        self.weights = weights
        self.portfolio_returns = self._calculate_portfolio_returns()
        
    def _calculate_portfolio_returns(self) -> pd.Series:
        """Calculate historical portfolio returns using current weights"""
        return self.returns.dot(self.weights)
    
    def calculate_var(
        self, 
        confidence_level: float = 0.95,
        method: str = 'historical'
    ) -> float:
        """
        Calculate Value at Risk (VaR) using various methods.
        
        Args:
            confidence_level (float): Confidence level for VaR
            method (str): Method to use ('historical', 'parametric', or 'monte_carlo')
            
        Returns:
            float: Value at Risk estimate
        """
        if method == 'historical':
            return -np.percentile(self.portfolio_returns, (1 - confidence_level) * 100)
        elif method == 'parametric':
            z_score = norm.ppf(confidence_level)
            return -(self.portfolio_returns.mean() - z_score * self.portfolio_returns.std())
        else:
            raise ValueError(f"Unsupported VaR method: {method}")
    
    def calculate_expected_shortfall(
        self, 
        confidence_level: float = 0.95
    ) -> float:
        """
        Calculate Expected Shortfall (Conditional VaR).
        
        Args:
            confidence_level (float): Confidence level
            
        Returns:
            float: Expected Shortfall estimate
        """
        var = self.calculate_var(confidence_level)
        return -self.portfolio_returns[self.portfolio_returns <= -var].mean()
    
    def calculate_risk_metrics(self) -> Dict[str, float]:
        """
        Calculate comprehensive set of risk metrics.
        
        Returns:
            Dict[str, float]: Dictionary of risk metrics
        """
        annual_factor = np.sqrt(252)  # Assuming daily data
        
        return {
            'volatility': self.portfolio_returns.std() * annual_factor,
            'var_95': self.calculate_var(0.95),
            'es_95': self.calculate_expected_shortfall(0.95),
            'skewness': self.portfolio_returns.skew(),
            'kurtosis': self.portfolio_returns.kurtosis(),
            'max_drawdown': self.calculate_max_drawdown(),
            'sortino_ratio': self.calculate_sortino_ratio()
        }
    
    def calculate_max_drawdown(self) -> float:
        """Calculate maximum drawdown of the portfolio"""
        cumulative_returns = (1 + self.portfolio_returns).cumprod()
        rolling_max = cumulative_returns.expanding().max()
        drawdowns = cumulative_returns / rolling_max - 1
        return float(drawdowns.min())
    
    def calculate_sortino_ratio(
        self, 
        risk_free_rate: float = 0.02,
        target_return: float = 0.0
    ) -> float:
        """
        Calculate Sortino Ratio (downside risk-adjusted return).
        
        Args:
            risk_free_rate (float): Annual risk-free rate
            target_return (float): Minimum acceptable return
            
        Returns:
            float: Sortino ratio
        """
        excess_returns = self.portfolio_returns - target_return
        downside_returns = excess_returns[excess_returns < 0]
        downside_std = np.sqrt(np.mean(downside_returns ** 2)) * np.sqrt(252)
        
        expected_return = self.portfolio_returns.mean() * 252
        return (expected_return - risk_free_rate) / downside_std if downside_std != 0 else np.inf