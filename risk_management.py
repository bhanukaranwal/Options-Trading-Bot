import numpy as np
import logging

class RiskManager:
    def __init__(self, config, portfolio):
        self.risk_config = config['risk']
        self.portfolio = portfolio

    def check_max_drawdown(self):
        """Checks if the portfolio has exceeded its maximum drawdown limit."""
        max_dd = self.risk_config['max_portfolio_drawdown_percent']
        current_drawdown = self.portfolio.get_drawdown()
        
        if current_drawdown > max_dd:
            logging.critical(f"CRITICAL: Max drawdown limit of {max_dd}% exceeded. Current drawdown: {current_drawdown:.2f}%. Halting all new trades.")
            return False
        return True

    def calculate_var(self, historical_returns, confidence_level=None):
        """
        Calculates Value-at-Risk (VaR) using the historical simulation method.
        """
        if confidence_level is None:
            confidence_level = self.risk_config['var_confidence_level']
            
        if len(historical_returns) < 50:
            logging.warning("Not enough historical data to calculate VaR accurately.")
            return 0
        
        # VaR is the percentile of the historical returns
        var = np.percentile(historical_returns, 100 * (1 - confidence_level))
        logging.info(f"Calculated VaR at {confidence_level*100}% confidence: {var:.2f}%")
        return abs(var)

    def check_trade_risk(self, potential_loss):
        """Checks if a single trade's risk exceeds the per-trade limit."""
        max_risk_pct = self.risk_config['max_trade_risk_percent']
        capital = self.portfolio.get_total_value()
        max_allowed_loss = capital * (max_risk_pct / 100)

        if potential_loss > max_allowed_loss:
            logging.warning(f"Trade rejected: Potential loss ({potential_loss:.2f}) exceeds max allowed risk per trade ({max_allowed_loss:.2f}).")
            return False
        return True
