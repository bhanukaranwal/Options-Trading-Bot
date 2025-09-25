import argparse
import asyncio
import logging
import yaml
import sys
from getpass import getpass

from backtrader.cerebro import Cerebro
from backtrader.feeds import PandasData

from strategy_engine import (
    StraddleStrategy,
    IronCondorStrategy,
    RSIMomentumStrategy,
)
from visualizations import generate_backtest_report
from execution_engine import KitePaperTrader, KiteLiveTrader
from data_fetcher import load_historical_data

# --- Logging Setup ---
def setup_logging(config):
    """Configures the logging for the application."""
    log_config = config.get('logging', {})
    logging.basicConfig(
        level=log_config.get('level', 'INFO'),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_config.get('file', 'trading_platform.log')),
            logging.StreamHandler(sys.stdout)
        ]
    )

# --- Main Application Logic ---
def run_backtest(config, args):
    """Runs the backtesting mode."""
    logging.info("--- Starting Backtesting Mode ---")
    
    # 1. Initialize backtrader engine
    cerebro = Cerebro()
    cerebro.broker.setcash(args.capital)
    cerebro.broker.setcommission(commission=config['backtesting']['commission_per_trade'])
    
    # 2. Load Data
    data_df = load_historical_data(config['backtesting']['historical_data_path'])
    data_feed = PandasData(dataname=data_df)
    cerebro.adddata(data_feed)
    
    # 3. Add Strategy
    strategy_map = {
        "straddle": StraddleStrategy,
        "iron_condor": IronCondorStrategy,
        "rsi_momentum": RSIMomentumStrategy,
    }
    if args.strategy not in strategy_map:
        raise ValueError(f"Strategy '{args.strategy}' not found.")
        
    cerebro.addstrategy(strategy_map[args.strategy])

    # 4. Add Analyzers
    cerebro.addanalyzer(backtrader.analyzers.SharpeRatio, _name='sharpe_ratio')
    cerebro.addanalyzer(backtrader.analyzers.DrawDown, _name='drawdown')
    cerebro.addanalyzer(backtrader.analyzers.TradeAnalyzer, _name='trade_analyzer')

    # 5. Run the backtest
    logging.info("Running backtest... This may take a while.")
    initial_portfolio_value = cerebro.broker.getvalue()
    results = cerebro.run()
    final_portfolio_value = cerebro.broker.getvalue()

    # 6. Generate Report
    logging.info("Backtest complete. Generating report...")
    strat = results[0]
    trade_analysis = strat.analyzers.trade_analyzer.get_analysis()
    
    performance_metrics = {
        "initial_capital": initial_portfolio_value,
        "final_capital": final_portfolio_value,
        "total_return_pct": ((final_portfolio_value - initial_portfolio_value) / initial_portfolio_value) * 100,
        "sharpe_ratio": strat.analyzers.sharpe_ratio.get_analysis().get('sharperatio', 0),
        "max_drawdown_pct": strat.analyzers.drawdown.get_analysis().max.drawdown,
        "total_trades": trade_analysis.total.total,
        "win_rate_pct": (trade_analysis.won.total / trade_analysis.total.total) * 100 if trade_analysis.total.total > 0 else 0,
    }

    print("\n--- Backtest Performance Metrics ---")
    for key, value in performance_metrics.items():
        print(f"{key.replace('_', ' ').title()}: {value:.2f}")

    generate_backtest_report(cerebro, performance_metrics, 'backtest_report.html')
    logging.info("Report saved to backtest_report.html")

async def run_paper_trading(config, args):
    """Runs the paper trading mode."""
    logging.info("--- Starting Paper Trading Mode ---")
    trader = KitePaperTrader(config, args.strategy, args.symbol, dry_run=args.dry_run)
    await trader.start()

async def run_live_trading(config, args):
    """Runs the live trading mode."""
    logging.warning("--- LIVE TRADING MODE ACTIVATED ---")
    logging.warning("This mode will execute REAL trades with REAL money.")
    
    if args.dry_run:
        logging.info("Dry-run mode is enabled. No real orders will be placed.")
    else:
        confirm = input("Are you sure you want to proceed with live trading? (yes/no): ")
        if confirm.lower() != 'yes':
            logging.info("Live trading aborted by user.")
            return
            
    trader = KiteLiveTrader(config, args.strategy, args.symbol, dry_run=args.dry_run)
    await trader.start()


# --- CLI Parser ---
def main():
    parser = argparse.ArgumentParser(description="High-Performance Options Trading Platform")
    parser.add_argument('--mode', type=str, required=True, choices=['backtest', 'paper', 'live'],
                        help="The mode to run the platform in.")
    parser.add_argument('--strategy', type=str, required=True,
                        help="The name of the strategy to execute (e.g., 'straddle').")
    parser.add_argument('--symbol', type=str, default='NIFTY',
                        help="The underlying symbol to trade (e.g., 'NIFTY').")
    parser.add_argument('--capital', type=float, default=100000.0,
                        help="Initial capital for backtesting.")
    parser.add_argument('--dry-run', action='store_true',
                        help="For paper/live modes, log trades without executing them.")
    
    args = parser.parse_args()

    # Load configuration
    try:
        with open('config.yaml', 'r') as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        logging.error("config.yaml not found. Please create it based on the README.")
        return

    setup_logging(config)
    
    if args.mode == 'backtest':
        run_backtest(config, args)
    elif args.mode == 'paper':
        asyncio.run(run_paper_trading(config, args))
    elif args.mode == 'live':
        asyncio.run(run_live_trading(config, args))

if __name__ == '__main__':
    main()
