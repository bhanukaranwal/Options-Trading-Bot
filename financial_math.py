import numpy as np
from scipy.stats import norm

# Note: The user prompt allowed standard libraries like scipy.stats, which is part
# of the scipy package often installed with numpy and pandas. If scipy is strictly
# forbidden, the norm.cdf can be approximated with the error function (math.erf).
# For this implementation, we assume `scipy.stats.norm` is available as it's a
# scientific computing standard.

def black_scholes_greeks(S, K, T, r, sigma, option_type='call'):
    """
    Calculates the Black-Scholes price and Greeks for a European option.

    Args:
        S (float): Current underlying price
        K (float): Option strike price
        T (float): Time to expiration in years
        r (float): Risk-free interest rate (annual)
        sigma (float): Volatility of the underlying asset (annual)
        option_type (str): 'call' or 'put'

    Returns:
        dict: A dictionary containing the price and Greeks (delta, gamma, theta, vega, rho).
    """
    if T <= 0 or sigma <= 0:
        # Handle expired or invalid options
        if option_type == 'call':
            price = max(0, S - K)
        else:
            price = max(0, K - S)
        return {'price': price, 'delta': 1 if S > K else 0, 'gamma': 0, 'theta': 0, 'vega': 0, 'rho': 0}

    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)

    if option_type == 'call':
        price = (S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2))
        delta = norm.cdf(d1)
        rho = K * T * np.exp(-r * T) * norm.cdf(d2)
    elif option_type == 'put':
        price = (K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1))
        delta = -norm.cdf(-d1)
        rho = -K * T * np.exp(-r * T) * norm.cdf(-d2)
    else:
        raise ValueError("Invalid option type. Must be 'call' or 'put'.")

    gamma = norm.pdf(d1) / (S * sigma * np.sqrt(T))
    vega = S * norm.pdf(d1) * np.sqrt(T) / 100 # Vega is per 1% change in vol
    theta = (- (S * norm.pdf(d1) * sigma) / (2 * np.sqrt(T)) -
             r * K * np.exp(-r * T) * (norm.cdf(d2) if option_type == 'call' else norm.cdf(-d2))) / 365 # per day

    return {
        'price': price,
        'delta': delta,
        'gamma': gamma,
        'theta': theta,
        'vega': vega,
        'rho': rho,
    }

def implied_volatility(market_price, S, K, T, r, option_type='call', max_iter=100, tol=1e-5):
    """
    Calculates the implied volatility using the Newton-Raphson method.
    """
    sigma = 0.2  # Initial guess for volatility
    for i in range(max_iter):
        greeks = black_scholes_greeks(S, K, T, r, sigma, option_type)
        price = greeks['price']
        vega = greeks['vega'] * 100 # Adjust vega back to its raw value

        if vega < 1e-6:
            return np.nan # Avoid division by zero

        diff = price - market_price
        if abs(diff) < tol:
            return sigma

        sigma = sigma - diff / vega

    return sigma if abs(diff) < tol else np.nan # Return NaN if not converged

