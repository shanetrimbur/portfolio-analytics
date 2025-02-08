from dash import Dash, html, dcc, Input, Output, State, callback_context
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from portfolio_analytics.optimizer import PortfolioOptimizer
from portfolio_analytics.risk_metrics import RiskAnalyzer

app = Dash(__name__, suppress_callback_exceptions=True)

# Enhanced sample data generation
def generate_sample_data():
    np.random.seed(42)
    dates = pd.date_range(start='2020-01-01', end='2023-12-31', freq='D')
    assets = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'BRK.A', 'JPM', 'JNJ', 'V', 'PG', 'XOM']
    
    # Generate more realistic returns with some correlation
    base_returns = np.random.normal(0.0005, 0.02, (len(dates), 1))
    asset_returns = np.random.normal(0.0005, 0.02, (len(dates), len(assets)))
    # Add some market correlation
    correlated_returns = 0.7 * base_returns + 0.3 * asset_returns
    
    returns = pd.DataFrame(
        correlated_returns,
        index=dates,
        columns=assets
    )
    return returns

app.layout = html.Div([
    # Navigation Tabs
    dcc.Tabs([
        dcc.Tab(label='Portfolio Optimization', children=[
            html.Div([
                html.H2("Portfolio Configuration", className="section-title"),
                
                # Enhanced Configuration Controls
                html.Div([
                    html.Div([
                        html.Label("Risk-Free Rate (%)"),
                        dcc.Input(
                            id='risk-free-rate',
                            type='number',
                            value=2.0,
                            step=0.1,
                            className="input-field"
                        )
                    ], className="control-group"),
                    
                    html.Div([
                        html.Label("Optimization Target"),
                        dcc.Dropdown(
                            id='optimization-target',
                            options=[
                                {'label': 'Maximum Sharpe Ratio', 'value': 'sharpe'},
                                {'label': 'Minimum Volatility', 'value': 'min_vol'},
                                {'label': 'Maximum Return', 'value': 'max_return'}
                            ],
                            value='sharpe',
                            className="dropdown-field"
                        )
                    ], className="control-group"),
                    
                    html.Div([
                        html.Label("Investment Constraints"),
                        dcc.Checklist(
                            id='investment-constraints',
                            options=[
                                {'label': 'No Short Selling', 'value': 'long_only'},
                                {'label': 'Max 20% per Asset', 'value': 'max_weight'},
                                {'label': 'Sector Limits', 'value': 'sector_limits'}
                            ],
                            value=['long_only'],
                            className="checklist-field"
                        )
                    ], className="control-group"),
                    
                    html.Button(
                        'Optimize Portfolio',
                        id='optimize-button',
                        className="action-button"
                    )
                ], className="controls-container"),
                
                # Interactive Results Display
                html.Div([
                    html.Div([
                        html.H3("Efficient Frontier"),
                        dcc.Graph(id='efficient-frontier-plot'),
                        html.Div(
                            "Click any point on the frontier to see portfolio details",
                            className="help-text"
                        )
                    ], className="chart-container"),
                    
                    html.Div([
                        html.H3("Portfolio Composition"),
                        dcc.Graph(id='weights-plot'),
                        html.Div(
                            "Drag to select multiple assets for detailed comparison",
                            className="help-text"
                        )
                    ], className="chart-container")
                ], className="results-container")
            ], className="tab-content")
        ]),
        
        dcc.Tab(label='Risk Analysis', children=[
            html.Div([
                html.H2("Risk Analytics", className="section-title"),
                
                # Risk Analysis Controls
                html.Div([
                    html.Div([
                        html.Label("Risk Metric"),
                        dcc.Dropdown(
                            id='risk-metric',
                            options=[
                                {'label': 'Value at Risk (VaR)', 'value': 'var'},
                                {'label': 'Expected Shortfall', 'value': 'es'},
                                {'label': 'Maximum Drawdown', 'value': 'drawdown'}
                            ],
                            value='var',
                            className="dropdown-field"
                        )
                    ], className="control-group"),
                    
                    html.Div([
                        html.Label("Confidence Level (%)"),
                        dcc.Slider(
                            id='confidence-level',
                            min=90,
                            max=99,
                            step=1,
                            value=95,
                            marks={i: f'{i}%' for i in range(90, 100, 2)},
                            className="slider-field"
                        )
                    ], className="control-group")
                ], className="controls-container"),
                
                # Risk Visualization
                html.Div([
                    dcc.Graph(id='risk-plot'),
                    html.Div(id='risk-metrics-table', className="metrics-container")
                ], className="results-container")
            ], className="tab-content")
        ]),
        
        dcc.Tab(label='Market Analysis', children=[
            html.Div([
                html.H2("Market Insights", className="section-title"),
                
                # Market Analysis Controls
                html.Div([
                    html.Div([
                        html.Label("Time Period"),
                        dcc.DatePickerRange(
                            id='date-range',
                            start_date='2020-01-01',
                            end_date='2023-12-31',
                            className="date-picker-field"
                        )
                    ], className="control-group"),
                    
                    html.Div([
                        html.Label("Analysis Type"),
                        dcc.Dropdown(
                            id='analysis-type',
                            options=[
                                {'label': 'Correlation Matrix', 'value': 'correlation'},
                                {'label': 'Rolling Beta', 'value': 'beta'},
                                {'label': 'Factor Analysis', 'value': 'factors'}
                            ],
                            value='correlation',
                            className="dropdown-field"
                        )
                    ], className="control-group")
                ], className="controls-container"),
                
                # Market Analysis Visualization
                dcc.Graph(id='market-analysis-plot')
            ], className="tab-content")
        ])
    ], className="tabs-container")
], className="dashboard-container")

# Add callbacks for the new interactive features
@app.callback(
    [Output('risk-plot', 'figure'),
     Output('risk-metrics-table', 'children')],
    [Input('risk-metric', 'value'),
     Input('confidence-level', 'value')]
)
def update_risk_analysis(risk_metric, confidence_level):
    returns = generate_sample_data()
    
    if risk_metric == 'var':
        # Create VaR visualization
        historical_returns = returns.sum(axis=1)
        var_level = np.percentile(historical_returns, 100 - confidence_level)
        
        fig = go.Figure()
        fig.add_trace(go.Histogram(
            x=historical_returns,
            name='Returns Distribution'
        ))
        fig.add_vline(
            x=var_level,
            line_dash="dash",
            annotation_text=f"VaR ({confidence_level}%)"
        )
        
        metrics_table = html.Table([
            html.Tr([html.Td("VaR"), html.Td(f"{-var_level:.4f}")]),
            html.Tr([html.Td("Confidence Level"), html.Td(f"{confidence_level}%")])
        ])
        
    elif risk_metric == 'drawdown':
        # Calculate and visualize drawdown
        cumulative_returns = (1 + returns.sum(axis=1)).cumprod()
        rolling_max = cumulative_returns.expanding().max()
        drawdowns = (cumulative_returns - rolling_max) / rolling_max
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=drawdowns.index,
            y=drawdowns,
            name='Drawdown'
        ))
        
        metrics_table = html.Table([
            html.Tr([html.Td("Maximum Drawdown"), html.Td(f"{drawdowns.min():.4f}")]),
            html.Tr([html.Td("Current Drawdown"), html.Td(f"{drawdowns.iloc[-1]:.4f}")])
        ])
    
    return fig, metrics_table

@app.callback(
    Output('market-analysis-plot', 'figure'),
    [Input('analysis-type', 'value'),
     Input('date-range', 'start_date'),
     Input('date-range', 'end_date')]
)
def update_market_analysis(analysis_type, start_date, end_date):
    returns = generate_sample_data()
    returns = returns.loc[start_date:end_date]
    
    if analysis_type == 'correlation':
        corr_matrix = returns.corr()
        fig = px.imshow(
            corr_matrix,
            labels=dict(x="Asset", y="Asset", color="Correlation"),
            x=returns.columns,
            y=returns.columns,
            color_continuous_scale="RdBu"
        )
    elif analysis_type == 'beta':
        # Calculate rolling beta against market (using first asset as market proxy)
        market_returns = returns.iloc[:, 0]
        betas = pd.DataFrame()
        
        for column in returns.columns[1:]:
            asset_returns = returns[column]
            rolling_cov = asset_returns.rolling(window=60).cov(market_returns)
            rolling_var = market_returns.rolling(window=60).var()
            betas[column] = rolling_cov / rolling_var
        
        fig = go.Figure()
        for column in betas.columns:
            fig.add_trace(go.Scatter(
                x=betas.index,
                y=betas[column],
                name=column
            ))
        fig.update_layout(title="Rolling 60-Day Beta")
    
    return fig

# Add this to your existing CSS
additional_css = '''
    .tabs-container {
        margin-top: 20px;
    }
    .tab-content {
        padding: 20px;
    }
    .control-group {
        margin-bottom: 15px;
    }
    .help-text {
        font-size: 0.9em;
        color: #666;
        margin-top: 5px;
    }
    .slider-field {
        padding: 20px 0;
    }
    .date-picker-field {
        margin: 10px 0;
    }
'''

if __name__ == '__main__':
    app.run_server(debug=True)