from dash import Dash, html, dcc, Input, Output, State
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from portfolio_analytics.optimizer import PortfolioOptimizer
from portfolio_analytics.risk_metrics import RiskAnalyzer

app = Dash(__name__)

# Sample data - in production, this would come from a database
def generate_sample_data():
    np.random.seed(42)
    dates = pd.date_range(start='2020-01-01', end='2023-12-31', freq='D')
    assets = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'BRK.A']
    
    returns = pd.DataFrame(
        np.random.normal(0.0005, 0.02, (len(dates), len(assets))),
        index=dates,
        columns=assets
    )
    return returns

# Layout
app.layout = html.Div([
    html.H1("Portfolio Analytics Dashboard", className="dashboard-title"),
    
    # Portfolio Configuration Section
    html.Div([
        html.H2("Portfolio Configuration"),
        html.Div([
            html.Label("Risk-Free Rate (%)"),
            dcc.Input(
                id='risk-free-rate',
                type='number',
                value=2.0,
                step=0.1,
                className="input-field"
            ),
            html.Button('Optimize Portfolio', id='optimize-button', className="action-button")
        ], className="config-controls")
    ], className="section"),
    
    # Results Section
    html.Div([
        # Efficient Frontier Plot
        html.Div([
            html.H3("Efficient Frontier"),
            dcc.Graph(id='efficient-frontier-plot')
        ], className="chart-container"),
        
        # Weights Distribution
        html.Div([
            html.H3("Optimal Portfolio Weights"),
            dcc.Graph(id='weights-plot')
        ], className="chart-container"),
        
        # Risk Metrics
        html.Div([
            html.H3("Risk Metrics"),
            html.Div(id='risk-metrics-table', className="metrics-container")
        ], className="metrics-section")
    ], className="results-section"),
    
    # Asset Correlation Heatmap
    html.Div([
        html.H3("Asset Correlation Matrix"),
        dcc.Graph(id='correlation-heatmap')
    ], className="chart-container"),
    
], className="dashboard-container")

# Callbacks
@app.callback(
    [Output('efficient-frontier-plot', 'figure'),
     Output('weights-plot', 'figure'),
     Output('correlation-heatmap', 'figure'),
     Output('risk-metrics-table', 'children')],
    [Input('optimize-button', 'n_clicks')],
    [State('risk-free-rate', 'value')]
)
def update_dashboard(n_clicks, risk_free_rate):
    # Get data
    returns = generate_sample_data()
    optimizer = PortfolioOptimizer(returns)
    
    # Calculate efficient frontier
    ef_data = optimizer.efficient_frontier(num_portfolios=100)
    
    # Optimize for Sharpe ratio
    optimal_weights, sharpe = optimizer.optimize_sharpe_ratio(risk_free_rate=risk_free_rate/100)
    
    # Create efficient frontier plot
    ef_fig = go.Figure()
    ef_fig.add_trace(go.Scatter(
        x=ef_data['volatility'],
        y=ef_data['return'],
        mode='lines',
        name='Efficient Frontier'
    ))
    ef_fig.update_layout(
        title="Portfolio Efficient Frontier",
        xaxis_title="Volatility",
        yaxis_title="Expected Return",
        template="plotly_white"
    )
    
    # Create weights plot
    weights_fig = go.Figure(data=[
        go.Bar(
            x=returns.columns,
            y=optimal_weights,
            name='Asset Weights'
        )
    ])
    weights_fig.update_layout(
        title="Optimal Portfolio Weights",
        xaxis_title="Assets",
        yaxis_title="Weight",
        template="plotly_white"
    )
    
    # Create correlation heatmap
    corr_matrix = returns.corr()
    heatmap_fig = px.imshow(
        corr_matrix,
        labels=dict(x="Asset", y="Asset", color="Correlation"),
        x=returns.columns,
        y=returns.columns,
        color_continuous_scale="RdBu"
    )
    heatmap_fig.update_layout(
        title="Asset Correlation Matrix",
        template="plotly_white"
    )
    
    # Calculate risk metrics
    risk_analyzer = RiskAnalyzer(returns, optimal_weights)
    metrics = risk_analyzer.calculate_risk_metrics()
    
    # Create metrics table
    metrics_table = html.Table([
        html.Thead(html.Tr([html.Th("Metric"), html.Th("Value")])),
        html.Tbody([
            html.Tr([html.Td(k), html.Td(f"{v:.4f}")]) 
            for k, v in metrics.items()
        ])
    ], className="metrics-table")
    
    return ef_fig, weights_fig, heatmap_fig, metrics_table

# Add CSS
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>Portfolio Analytics Dashboard</title>
        {%favicon%}
        {%css%}
        <style>
            .dashboard-container {
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                font-family: Arial, sans-serif;
            }
            .dashboard-title {
                color: #2c3e50;
                text-align: center;
                margin-bottom: 30px;
            }
            .section {
                margin-bottom: 30px;
                padding: 20px;
                background: white;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            .chart-container {
                margin-bottom: 30px;
            }
            .metrics-table {
                width: 100%;
                border-collapse: collapse;
            }
            .metrics-table th, .metrics-table td {
                padding: 12px;
                text-align: left;
                border-bottom: 1px solid #ddd;
            }
            .metrics-table th {
                background-color: #f8f9fa;
            }
            .action-button {
                background-color: #3498db;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 4px;
                cursor: pointer;
            }
            .action-button:hover {
                background-color: #2980b9;
            }
            .input-field {
                padding: 8px;
                margin: 10px;
                border: 1px solid #ddd;
                border-radius: 4px;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

if __name__ == '__main__':
    app.run_server(debug=True)