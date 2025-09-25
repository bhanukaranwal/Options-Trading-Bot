import plotly.graph_objects as go
from plotly.subplots import make_subplots

def generate_backtest_report(cerebro, metrics, filename='backtest_report.html'):
    """
    Generates an interactive HTML report of the backtest results using Plotly.
    """
    strat = cerebro.runstrats[0][0]
    portfolio_values = strat.analyzers.drawdown.get_analysis().portfolio
    
    # Create subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=("Equity Curve", "Drawdown", "Performance Metrics", "Payoff Diagram (Placeholder)"),
        specs=[[{"rowspan": 2}, {}], [None, {}]],
        vertical_spacing=0.15
    )

    # 1. Equity Curve
    fig.add_trace(go.Scatter(
        x=list(range(len(portfolio_values))),
        y=portfolio_values,
        mode='lines',
        name='Portfolio Value'
    ), row=1, col=1)

    # 2. Drawdown
    drawdown_data = strat.analyzers.drawdown.get_analysis().drawdown
    fig.add_trace(go.Scatter(
        x=list(range(len(drawdown_data))),
        y=drawdown_data,
        mode='lines',
        name='Drawdown (%)',
        fill='tozeroy',
        line=dict(color='red')
    ), row=1, col=2)
    
    # 3. Performance Metrics Table
    fig.add_trace(go.Table(
        header=dict(values=['Metric', 'Value']),
        cells=dict(values=[list(metrics.keys()), [f'{v:.2f}' for v in metrics.values()]])
    ), row=2, col=2)

    # Update layout
    fig.update_layout(
        title_text="Backtest Performance Report",
        height=800,
        showlegend=False
    )
    
    fig.write_html(filename)
