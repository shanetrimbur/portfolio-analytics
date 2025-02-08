/*
* File: docs/technical/quantitative_models.md
* Path: portfolio-analytics/docs/technical/quantitative_models.md
* Description: Technical documentation of implemented and planned quantitative finance models
* Author: Shane Trimbur
* Last Updated: 2024-02-07
*/

# Quantex Portfolio Analytics
## Quantitative Models & Implementation Details

## Currently Implemented Models

### 1. Portfolio Optimization
*Implementation: src/portfolio_analytics/optimizer.py*

#### Modern Portfolio Theory (MPT)
```python
def optimize_portfolio(returns: np.ndarray, target_return: float) -> np.ndarray:
    """
    Implements Markowitz portfolio optimization:
    
    min w^T Σ w  (minimize portfolio variance)
    s.t. w^T μ ≥ r_target  (return constraint)
         Σw_i = 1  (budget constraint)
         w_i ≥ 0  (long-only constraint)
    """
```

Mathematical formulation:

$$\min_w \sigma^2_p = w^T\Sigma w$$

Subject to:

$$\sum_{i=1}^n w_i = 1 \text{ and } w^T\mu \geq \mu_{target}$$

### 2. Risk Analytics
*Implementation: src/portfolio_analytics/risk_metrics.py*

#### Value at Risk (VaR)
```python
def calculate_var(returns: np.ndarray, confidence: float = 0.95) -> float:
    """
    Calculates parametric VaR:
    VaR_α = -μ - σΦ^{-1}(α)
    """
```

$$\text{VaR}_{\alpha} = -\mu - \sigma\Phi^{-1}(\alpha)$$

#### Expected Shortfall
```python
def calculate_cvar(returns: np.ndarray, confidence: float = 0.95) -> float:
    """
    Calculates Conditional VaR (Expected Shortfall):
    CVaR_α = E[R|R ≤ -VaR_α]
    """
```

$$\text{CVaR}_{\alpha} = -\mathbb{E}[R|R \leq -\text{VaR}_{\alpha}]$$

## Planned Implementations (Q2 2024)

### 1. Factor Models
*Planned Implementation: src/portfolio_analytics/factor_models.py*

#### Fama-French Five-Factor Model
Will implement factor decomposition:

$$R_i - R_f = \alpha_i + \beta_i(R_m - R_f) + s_i\text{SMB} + h_i\text{HML} + r_i\text{RMW} + c_i\text{CMA} + \epsilon_i$$

Features:
- Factor exposure calculation
- Risk decomposition
- Attribution analysis
- Factor timing signals

### 2. Fixed Income Analytics
*Planned Implementation: src/portfolio_analytics/fixed_income.py*

#### Yield Curve Analysis

$$P = \sum_{t=1}^T \frac{C}{(1+r_t)^t} + \frac{F}{(1+r_T)^T}$$

Features:
- Duration calculation
- Convexity analysis
- Key rate duration
- Yield curve construction using splines

### 3. Derivatives Pricing
*Planned Implementation: src/portfolio_analytics/derivatives.py*

#### Black-Scholes Implementation

$$C = S_0N(d_1) - Ke^{-rT}N(d_2)$$

Where:

$$d_1 = \frac{\ln(S_0/K) + (r + \sigma^2/2)T}{\sigma\sqrt{T}}$$

$$d_2 = d_1 - \sigma\sqrt{T}$$

Features:
- Greeks calculation (Δ, Γ, Θ, ν, ρ)
- Implied volatility surface
- American options using binomial trees

## Machine Learning Integration (Q3 2024)
*Planned Implementation: src/portfolio_analytics/ml_models.py*

### 1. Deep Learning for Asset Pricing
Neural network architecture for return prediction:

$$f(x) = \sigma(\sum_{i=1}^n w_i x_i + b)$$

Features:
- LSTM for time series prediction
- Attention mechanisms for factor importance
- Adversarial training for robustness

### 2. Regime Detection
Hidden Markov Models for market regimes:

$$P(S_t = j|S_{t-1} = i) = a_{ij}$$
$$P(O_t|S_t) = \mathcal{N}(\mu_{S_t}, \sigma^2_{S_t})$$

## High-Performance Computing
*Implementation: src/portfolio_analytics/parallel/*

### Current Optimizations
```python
@numba.jit(nopython=True)
def parallel_covariance(returns: np.ndarray) -> np.ndarray:
    """
    Optimized covariance calculation using Numba
    """
```

### Planned Optimizations
- GPU acceleration for Monte Carlo
- Distributed computing for large portfolios
- Real-time optimization using C++ backends

## API Integration
*Implementation: src/api/*

### Current Endpoints
```python
@app.get("/api/v1/portfolio/optimize")
async def optimize_portfolio(
    returns: List[float],
    constraints: Dict[str, Any]
) -> Dict[str, Any]:
    """
    REST endpoint for portfolio optimization
    """
```

### Planned Endpoints
- Real-time market data integration
- WebSocket support for streaming data
- OAuth2 authentication

## Testing & Validation
*Implementation: tests/*

### Current Coverage
- Unit tests for all mathematical models
- Integration tests for API endpoints
- Performance benchmarks

### Validation Methods
- Backtesting against historical data
- Monte Carlo validation
- Stress testing scenarios

## References & Dependencies

### Mathematical References
1. Markowitz, H.M. (1952). "Portfolio Selection"
2. Fama, E.F., French, K.R. (2015). "Five-Factor Model"
3. Black, F., Scholes, M. (1973). "Option Pricing"

### Tech Stack
- Python 3.10+
- NumPy, Pandas, SciPy
- FastAPI for REST endpoints
- PyTorch for ML models

### Performance Metrics
- Optimization time: O(n²) for n assets
- Real-time risk calculation: < 100ms
- Monte Carlo simulation: 10⁶ paths/second

## Contribution Guidelines
See CONTRIBUTING.md for:
- Code style guide
- Testing requirements
- Documentation standards
- Pull request process