from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict
import numpy as np
import pandas as pd
from portfolio_analytics.optimizer import PortfolioOptimizer

app = FastAPI(
    title="Portfolio Analytics API",
    description="API for portfolio optimization and risk analysis",
    version="1.0.0"
)

class OptimizationRequest(BaseModel):
    returns_data: Dict[str, List[float]]
    risk_free_rate: float = 0.02

class OptimizationResponse(BaseModel):
    optimal_weights: Dict[str, float]
    metrics: Dict[str, float]

@app.post("/optimize/sharpe", response_model=OptimizationResponse)
async def optimize_portfolio(request: OptimizationRequest):
    """
    Optimize portfolio weights to maximize Sharpe ratio
    """
    try:
        # Convert dict to DataFrame
        returns_df = pd.DataFrame(request.returns_data)
        
        # Initialize optimizer
        optimizer = PortfolioOptimizer(returns_df)
        
        # Optimize portfolio
        weights, sharpe = optimizer.optimize_sharpe_ratio(
            risk_free_rate=request.risk_free_rate
        )
        
        # Calculate metrics
        metrics = optimizer.calculate_metrics(weights)
        
        # Prepare response
        return OptimizationResponse(
            optimal_weights=dict(zip(returns_df.columns, weights)),
            metrics=metrics
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {"status": "healthy"}