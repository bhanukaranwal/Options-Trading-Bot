import asyncio
import logging
import base64
from kiteconnect import KiteConnect, KiteTicker

class BaseTrader:
    """Base class for paper and live trading engines."""
    def __init__(self, config, strategy, symbol, dry_run=False):
        self.config = config
        self.api_config = config['api']
        self.strategy_name = strategy
        self.symbol = symbol
        self.dry_run = dry_run
        
        api_key = self.api_config['api_key']
        # For production, use a secure vault. This is a placeholder.
        api_secret = base64.b64decode(self.api_config['api_secret_base64_encoded']).decode('utf-8')
        
        self.kite = KiteConnect(api_key=api_key)
        self.kite.set_access_token(self.api_config['access_token'])
        
        self.kws = KiteTicker(api_key, self.api_config['access_token'])
        self.kws.on_ticks = self.on_ticks
        self.kws.on_connect = self.on_connect
        
        logging.info(f"Trader initialized for {symbol} with strategy {strategy}. Dry run: {self.dry_run}")
        
    async def start(self):
        logging.info("Starting trader...")
        self.kws.connect(threaded=True)
        # Keep the main thread alive
        while True:
            await asyncio.sleep(1)

    def on_ticks(self, ws, ticks):
        logging.debug(f"Ticks received: {ticks}")
        # Strategy logic would be implemented here, processing ticks
        # and making trade decisions.
        # For this example, we just log the tick reception.

    def on_connect(self, ws, response):
        logging.info("WebSocket connected. Subscribing to instruments.")
        # Example: Subscribe to NIFTY 50 index
        # You need to get the instrument token first.
        # instruments = self.kite.instruments("NFO")
        # token = [inst['instrument_token'] for inst in instruments if inst['tradingsymbol'] == self.symbol][0]
        token = 256265 # NIFTY 50 Index token (example)
        ws.subscribe([token])
        ws.set_mode(ws.MODE_FULL, [token])

    def place_order(self, tradingsymbol, quantity, transaction_type, order_type, price=None):
        """Places an order through the Kite API."""
        try:
            if self.dry_run:
                logging.info(f"[DRY RUN] Order: {transaction_type} {quantity} of {tradingsymbol} at {price or 'MARKET'}")
                return "dry_run_order_id"

            order_id = self.kite.place_order(
                variety=self.kite.VARIETY_REGULAR,
                exchange=self.config['symbols'][self.symbol]['exchange'],
                tradingsymbol=tradingsymbol,
                transaction_type=transaction_type,
                quantity=quantity,
                product=self.kite.PRODUCT_MIS,
                order_type=order_type,
                price=price,
                validity=self.kite.VALIDITY_DAY
            )
            logging.info(f"Order placed successfully. Order ID: {order_id}")
            return order_id
        except Exception as e:
            logging.error(f"Order placement failed: {e}")
            return None


class KitePaperTrader(BaseTrader):
    """Paper trading engine using Kite Connect sandbox."""
    def __init__(self, config, strategy, symbol, dry_run=True):
        super().__init__(config, strategy, symbol, dry_run=True) # Paper trading is always a dry run
        logging.info("Paper Trader initialized. All trades will be simulated.")

class KiteLiveTrader(BaseTrader):
    """Live trading engine."""
    def __init__(self, config, strategy, symbol, dry_run=False):
        super().__init__(config, strategy, symbol, dry_run)
        logging.info("Live Trader initialized.")
