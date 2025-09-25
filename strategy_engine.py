import backtrader as bt
import backtrader.indicators as btind
from financial_math import black_scholes_greeks

class BaseStrategy(bt.Strategy):
    """Base class for all options strategies."""
    params = (
        ('symbol_config', None),
        ('risk_config', None),
    )
    
    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print(f'{dt.isoformat()} - {txt}')

    def __init__(self):
        self.underlying = self.datas[0]
        self.lot_size = self.p.symbol_config['lot_size']
        self.risk_params = self.p.risk_config
        self.order = None

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
        if order.status in [order.Completed]:
            self.log(f'ORDER COMPLETED: {order.executed.price:.2f}, Size: {order.executed.size}')
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')
        self.order = None

class StraddleStrategy(BaseStrategy):
    """
    A simple long straddle strategy. Enters a straddle on the first bar.
    This is for demonstration; a real strategy would have better entry logic.
    """
    def next(self):
        if self.position:
            return # Only enter once

        # Find ATM strike
        atm_strike = round(self.underlying.close[0] / 100) * 100
        
        # For backtesting, we simulate option prices. A real implementation
        # would fetch live option data.
        self.log(f"Entering Long Straddle at ATM strike: {atm_strike}")
        
        # Simulate buying a call and a put
        # In backtrader, you'd typically have separate data feeds for each option
        # Here we just simulate the buy orders for accounting.
        self.buy(size=self.lot_size) # Represents the call
        self.buy(size=self.lot_size) # Represents the put
        self.log(f'BUY EXECUTED for Straddle, Price: {self.underlying.close[0]:.2f}, Size: {self.lot_size * 2}')

class IronCondorStrategy(BaseStrategy):
    """Sells an Iron Condor, assuming a range-bound market."""
    def next(self):
        if self.position:
            return
        
        price = self.underlying.close[0]
        # Example logic: Sell 200 points OTM call/put, buy 300 points OTM
        sell_put_strike = round((price * 0.98) / 50) * 50
        buy_put_strike = round((price * 0.97) / 50) * 50
        sell_call_strike = round((price * 1.02) / 50) * 50
        buy_call_strike = round((price * 1.03) / 50) * 50

        self.log(f"Entering Iron Condor: Sell {sell_put_strike}P & {sell_call_strike}C, Buy {buy_put_strike}P & {buy_call_strike}C")
        # In a real scenario, each leg is a separate order
        self.sell(size=self.lot_size) # Net credit strategy
        
class RSIMomentumStrategy(BaseStrategy):
    """A directional strategy using RSI."""
    params = (('rsi_period', 14), ('rsi_overbought', 70), ('rsi_oversold', 30))

    def __init__(self):
        super().__init__()
        self.rsi = btind.RelativeStrengthIndex(period=self.p.rsi_period)

    def next(self):
        if self.order:
            return

        if not self.position:
            if self.rsi < self.p.rsi_oversold:
                self.log(f'RSI oversold ({self.rsi[0]:.2f}). Buying Call Option.')
                self.order = self.buy(size=self.lot_size)
        else:
            if self.rsi > self.p.rsi_overbought:
                self.log(f'RSI overbought ({self.rsi[0]:.2f}). Closing position.')
                self.order = self.close()
