import unittest
import numpy as np

from financial_math import black_scholes_greeks, implied_volatility

class TestFinancialMath(unittest.TestCase):

    def setUp(self):
        """Set up common parameters for tests."""
        self.S = 100  # Underlying price
        self.K = 100  # Strike price
        self.T = 1.0  # 1 year to expiry
        self.r = 0.05 # 5% risk-free rate
        self.sigma = 0.2 # 20% volatility

    def test_black_scholes_call(self):
        """Test Black-Scholes call option pricing."""
        greeks = black_scholes_greeks(self.S, self.K, self.T, self.r, self.sigma, 'call')
        # Expected values from a known BS calculator
        self.assertAlmostEqual(greeks['price'], 10.45, delta=0.01)
        self.assertAlmostEqual(greeks['delta'], 0.636, delta=0.001)
        self.assertAlmostEqual(greeks['gamma'], 0.018, delta=0.001)
        self.assertAlmostEqual(greeks['vega'], 0.38, delta=0.01) # vega per 1%
        self.assertAlmostEqual(greeks['theta'], -0.017, delta=0.001) # theta per day

    def test_black_scholes_put(self):
        """Test Black-Scholes put option pricing."""
        greeks = black_scholes_greeks(self.S, self.K, self.T, self.r, self.sigma, 'put')
        # Expected values from a known BS calculator
        self.assertAlmostEqual(greeks['price'], 5.57, delta=0.01)
        self.assertAlmostEqual(greeks['delta'], -0.363, delta=0.001)

    def test_implied_volatility(self):
        """Test the implied volatility solver."""
        market_price = 10.45
        iv = implied_volatility(market_price, self.S, self.K, self.T, self.r, 'call')
        self.assertAlmostEqual(iv, self.sigma, delta=1e-4)

    def test_edge_cases(self):
        """Test edge cases like expired options."""
        # Expired in-the-money call
        greeks = black_scholes_greeks(S=110, K=100, T=0, r=self.r, sigma=self.sigma, option_type='call')
        self.assertEqual(greeks['price'], 10) # Intrinsic value
        self.assertEqual(greeks['delta'], 1)

if __name__ == '__main__':
    unittest.main()
