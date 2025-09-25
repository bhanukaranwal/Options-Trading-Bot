# High-Performance Python Options Trading Platform for Indian Markets

This repository contains a complete, CLI-based options trading platform tailored specifically for the Indian options market (NSE/BSE). It is designed for high-performance backtesting, paper trading, and live execution of algorithmic options strategies. The platform is built with a modular architecture and emphasizes speed, reliability, and adherence to professional coding standards.

<br>

> **🛑 Financial Risk Disclaimer**
>
> This software is provided for **educational and research purposes only**. It is **NOT financial advice**. Trading in financial instruments, especially derivatives like options, involves substantial risk and is not suitable for all investors. You could lose all or more of your initial investment. The authors and distributors of this software assume **no responsibility** for any financial losses incurred from its use. **Use at your own risk.**

---

### **Table of Contents**

1.  [**Core Features**](#core-features)
2.  [**Architecture Overview**](#architecture-overview)
3.  [**Technology Stack**](#technology-stack)
4.  [**Installation and Setup**](#installation-and-setup)
5.  [**Configuration**](#configuration)
6.  [**How to Run the Platform**](#how-to-run-the-platform)
    *   [Generate Sample Data](#1-generate-sample-data)
    *   [Run a Backtest](#2-run-a-backtest)
    *   [Run in Paper Trading Mode](#3-run-in-paper-trading-mode)
    *   [Run in Live Trading Mode](#4-run-in-live-trading-mode)
7.  [**Available Strategies**](#available-strategies)
8.  [**Extending the Platform**](#extending-the-platform)
    *   [Adding a New Strategy](#adding-a-new-strategy)
9.  [**Running Unit Tests**](#running-unit-tests)
10. [**Contributing**](#contributing)
11. [**License**](#license)

***

## **Core Features**

*   **Multiple Operating Modes**: Seamlessly switch between **Backtesting**, **Paper Trading**, and **Live Trading**.
*   **Modular and Extensible Architecture**: Clean separation of concerns (data, strategy, execution, risk, visualization) makes the code easy to maintain and extend.[1]
*   **High-Performance Backtesting**: Leverages the powerful `backtrader` engine for robust event-driven simulations and `numpy`/`pandas` for fast, vectorized analysis.
*   **Indian Market Specifics**: Pre-configured for NSE indices like **NIFTY**, **BANKNIFTY**, and **FINNIFTY**, with correct lot sizes, expiry conventions, and brokerage simulation.
*   **Advanced Strategy Support**: Comes with pre-built templates for common options strategies (Straddle, Iron Condor) and technical indicator-based models (RSI Momentum).
*   **Integrated Risk Management**: Features built-in controls for Value-at-Risk (VaR), maximum drawdown limits, and position sizing to enforce trading discipline.
*   **Interactive Visualizations**: Generates rich, interactive reports using `Plotly` for detailed performance analysis, including equity curves, drawdown charts, and key metrics.
*   **Real-Time Connectivity**: Integrates with the **Zerodha Kite API** for both paper trading (sandbox) and live trade execution via a WebSocket connection.

## **Architecture Overview**

The platform is designed as a modular system where each component has a specific responsibility:

*   `main.py`: The central entry point that parses command-line arguments and orchestrates the application flow.
*   `config.yaml`: A centralized YAML file for all user-configurable parameters, including API keys, trading symbols, and risk settings.
*   `data_fetcher.py`: Handles all data-related tasks, including generating sample historical data and fetching live data streams.
*   `financial_math.py`: Contains pure mathematical functions for options pricing (Black-Scholes), Greeks calculation, and Implied Volatility (IV) solving.
*   `strategy_engine.py`: Defines the base strategy class and implementations of specific trading algorithms using `backtrader`.
*   `execution_engine.py`: Manages order placement, modification, and cancellation for paper and live trading modes via the broker API.
*   `risk_management.py`: Enforces portfolio-level and trade-level risk rules before and during trade execution.
*   `visualizations.py`: Generates all charts and reports for performance analysis.
*   `tests/`: A dedicated directory for unit tests to ensure the correctness of critical components like financial calculations.

## **Technology Stack**

The platform is built using Python 3.12 and a minimal set of powerful, pre-approved libraries. No other external dependencies are required.

*   **Core Language**: Python 3.12
*   **Data Manipulation**: `pandas`, `numpy`
*   **Backtesting Engine**: `backtrader`
*   **Technical Analysis**: `ta-lib`
*   **API Communication**: `requests`, `asyncio`
*   **Visualization**: `plotly`, `matplotlib`
*   **Configuration**: `pyyaml`
*   **Broker API**: `kiteconnect`

## **Installation and Setup**

1.  **Clone the Repository**:
    ```bash
    git clone https://github.com/your-username/options-trading-platform.git
    cd options-trading-platform
    ```

2.  **Prerequisites**:
    Ensure you have Python 3.12+ installed. The platform relies on a specific set of libraries that must be present in your environment.

3.  **Install Dependencies**:
    You can install all required packages using `pip`:
    ```bash
    pip install pandas numpy matplotlib plotly TA-Lib backtrader requests pyyaml kiteconnect
    ```
    > **Note on TA-Lib**: The `TA-Lib` library can have a complex installation process as it depends on the underlying C library. Please follow the [official TA-Lib installation guide](https://mrjbq7.github.io/ta-lib/install.html) for your operating system **before** running the pip command.

## **Configuration**

All platform settings are managed centrally in the `config.yaml` file. Before running the application, you must configure it properly:[3]

1.  **API Credentials (for Paper/Live Trading)**:
    *   Create an app on the [Zerodha Kite Connect Developer](https://kite.trade) portal to get your `api_key` and `api_secret`.
    *   Generate a daily `access_token` using the Kite Connect API flow.
    *   Update these values in `config.yaml`.

    > **🔒 Security Best Practice**: The `config.yaml` provides a simple Base64 encoding for the API secret as a placeholder. In a production environment, **never store plain-text secrets in configuration files**. Use a secure secret management system like HashiCorp Vault, AWS Secrets Manager, or environment variables.

2.  **Trading Parameters**:
    *   Adjust symbols (`NIFTY`, `BANKNIFTY`), default capital, and other parameters to fit your trading plan.

## **How to Run the Platform**

The application is run from the command line via the `main.py` script. The two main arguments are `--mode` and `--strategy`.

#### **1. Generate Sample Data**

For backtesting, you need historical data. The platform includes a script to generate a sample one-year, 1-minute OHLC dataset for the NIFTY index.

```bash
python data_fetcher.py --generate-sample-data
```

This command will create a file named `nifty_options_data.csv` in your project's root directory.

#### **2. Run a Backtest**

Execute a strategy against the historical dataset to evaluate its performance without any financial risk.

```bash
python main.py --mode backtest --strategy straddle --symbol NIFTY --capital 100000
```

*   `--mode backtest`: Runs the backtesting engine.
*   `--strategy straddle`: Specifies the strategy to test.
*   `--symbol NIFTY`: Defines the underlying instrument.
*   `--capital 100000`: Sets the initial virtual capital for the simulation.

The backtest will print a performance summary to the console and generate an interactive HTML report named `backtest_report.html`.

#### **3. Run in Paper Trading Mode**

Simulate live trading using the Zerodha Kite Connect sandbox environment. This mode connects to the live market data feed but executes trades against a virtual account.

```bash
python main.py --mode paper --strategy rsi_momentum --symbol BANKNIFTY
```

All actions, including order placements and strategy signals, will be logged in `trading_platform.log`.

#### **4. Run in Live Trading Mode**

> **⚠️ EXTREME CAUTION**: This mode executes **real trades with real money** in your brokerage account. Ensure your strategy, risk parameters, and API configuration are flawless before proceeding.

First, run with the `--dry-run` flag to verify the logic without sending orders to the exchange:

```bash
python main.py --mode live --strategy iron_condor --symbol NIFTY --dry-run
```

Once you are confident, remove the `--dry-run` flag to go live. The application will require explicit confirmation before activating.

```bash
python main.py --mode live --strategy iron_condor --symbol NIFTY
```

## **Available Strategies**

The platform comes with three pre-built strategies in `strategy_engine.py`:

*   `straddle`: A classic non-directional volatility strategy that buys an at-the-money (ATM) call and put.
*   `iron_condor`: A range-bound, risk-defined strategy that profits from low volatility.
*   `rsi_momentum`: A directional strategy that enters trades based on signals from the Relative Strength Index (RSI) indicator.

## **Extending the Platform**

The modular design makes it easy to add new functionalities.

#### **Adding a New Strategy**

1.  Open `strategy_engine.py`.
2.  Create a new class that inherits from `BaseStrategy`.
3.  Implement your trading logic within the `next()` method, which is called on every new bar of data.
4.  Use `self.buy()` or `self.sell()` to create orders.
5.  Import and register your new strategy class in `main.py`'s `strategy_map`.

## **Running Unit Tests**

To ensure the core financial calculations are accurate, you can run the provided unit tests:

```bash
python -m unittest tests/test_financial_math.py
```

## **Contributing**

Contributions are welcome! If you would like to contribute, please follow these steps:

1.  Fork the repository.
2.  Create a new branch for your feature or bug fix (`git checkout -b feature/your-feature-name`).
3.  Commit your changes (`git commit -m 'Add some feature'`).
4.  Push to the branch (`git push origin feature/your-feature-name`).
5.  Open a Pull Request.

## **License**

This project is licensed under the MIT License. See the `LICENSE` file for more details.
