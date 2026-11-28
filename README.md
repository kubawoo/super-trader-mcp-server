# super-trader-mcp-server

![Version](https://img.shields.io/github/v/release/kubawoo/super-trader-mcp-server?style=flat-square)
![License](https://img.shields.io/github/license/kubawoo/super-trader-mcp-server?style=flat-square)
![Python](https://img.shields.io/badge/python-3.13%2B-blue?style=flat-square)

MCP Server offering a comprehensive set of tools for traders and investors.

## Features

- **Real-time Stock/ETF Prices**: Get current market prices using `yfinance`.
- **ETF Insights**: Retrieve top holdings and equity valuation metrics (P/E, P/B, etc.) for ETFs.
- **Company Info**: Look up sector, industry, market cap, and employee count.
- **Company News**: Latest news articles for any ticker.
- **Dividend Analysis**: Full dividend history, rates, yields, and key dates.
- **Financial Statements**: Income statement, balance sheet, cash flow (annual, quarterly, TTM).
- **Options**: Expiration dates, full option chains, ATM options, strike-range filtering.
- **Earnings**: Dates, history, analyst estimates, surprises.
- **Analyst Data**: Price targets, recommendation trends, upgrades/downgrades.
- **Correlation & Beta**: Pearson correlation and beta/alpha/R-squared vs benchmark (default SPY).
- **Index Constituents**: NASDAQ 100, S&P 500, WIG20, mWIG40, sWIG80 with weights/sectors.
- **Historical Data**: OHLCV bars via tools or CSV resource.
- **Time Utilities**: Easy access to current date and time.
- **MCP-native**: Compatible with any MCP client (Claude Desktop, Cursor, llama.cpp, etc.).

## Running released version

**Note: Instructions are provided for Linux/bash. Similar steps apply to other platforms.**

```bash
# Download the latest release package
wget https://github.com/kubawoo/super-trader-mcp-server/releases/download/0.1.0/super_trader_mcp_server-0.1.0-py3-none-any.whl

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install the package
pip install super_trader_mcp_server-0.1.0-py3-none-any.whl

# (Optional) Set server port
export FASTMCP_PORT=8000

# Start the server
python3 -m super_trader_mcp_server.main

# (Optional) Verify health check
curl http://localhost:8000/health
```

## Running from source code

### Prerequisites
- Python 3.13+
- [uv](https://github.com/astral-sh/uv) (Python package manager)
- git

### Setup
```bash
# Clone the repository
git clone https://github.com/kubawoo/super-trader-mcp-server.git
cd super-trader-mcp-server

# (Optional) Set server port
export FASTMCP_PORT=8000

# Start server using uv
uv run super-trader

# (Optional) Verify health check
curl http://localhost:8000/health
```

## Transport

The server uses **Streamable HTTP** transport (not stdio). The MCP endpoint is at `http://localhost:<port>/mcp`. Clients connect via SSE or JSON-RPC over HTTP using the `mcp-session-id` header returned from the `initialize` handshake.

## Configuration

The server can be configured via environment variables:

| Variable | Description | Default |
| :--- | :--- | :--- |
| `FASTMCP_PORT` | The port on which the MCP server runs | `8000` |

## Integration

For instructions on setting up a client like [llama.cpp](docs/llama_cpp_integration.md), see the dedicated documentation.

## Available tools

| Tool Name | Description | Parameters | Defaults |
| :--- | :--- | :--- | :--- |
| `get_current_time` | Returns the current system time | `fmt` (str) | `%H:%M` |
| `get_current_date` | Returns the current system date | `fmt` (str) | `%Y-%m-%d` |
| `get_current_stock_price` | Returns the current price of a stock or ETF (regular, pre, post market) | `ticker` (str) | - |
| `get_historical_quotes` | Returns OHLCV historical price data | `ticker`, `period`, `interval` | `1y`, `1d` |
| `get_top_holdings` | Returns the top holdings of an ETF/fund | `ticker` (str) | - |
| `get_etf_equity_stats` | Returns equity valuation metrics (P/E, P/B, P/S, P/CF) for an ETF vs category | `ticker` (str) | - |
| `get_company_info` | Returns company profile, financials, valuation, dividends | `ticker` (str) | - |
| `get_company_news` | Returns latest news articles for a ticker | `ticker` (str) | - |
| `get_dividend_details` | Returns dividend history, rates, yields, ex-dates | `ticker` (str) | - |
| `get_income_statement` | Returns income statement (annual/quarterly/TTM) | `ticker`, `quarterly`, `ttm` | `false`, `false` |
| `get_balance_sheet` | Returns balance sheet (annual/quarterly) | `ticker`, `quarterly` | `false` |
| `get_cash_flow` | Returns cash flow statement (annual/quarterly/TTM) | `ticker`, `quarterly`, `ttm` | `false`, `false` |
| `get_option_expirations` | Returns available option expiration dates | `ticker` (str) | - |
| `get_option_chain` | Returns full option chain (calls & puts) for an expiration | `ticker`, `expiration_date` | - |
| `get_atm_options` | Returns ATM options + nearby strikes | `ticker`, `expiration_date?`, `nearby_strikes?` | nearest exp, 3 |
| `get_options_by_strike_range` | Returns option chain filtered by strike range | `ticker`, `expiration_date`, `min_strike?`, `max_strike?` | - |
| `get_earnings_dates` | Returns upcoming & historical earnings dates with estimates | `ticker` (str) | - |
| `get_earnings_history` | Returns quarterly earnings actuals vs estimates | `ticker` (str) | - |
| `get_earnings_estimates` | Returns analyst EPS estimates for current/next quarter/year | `ticker` (str) | - |
| `get_analyst_price_targets` | Returns high/low/mean/median/current price targets | `ticker` (str) | - |
| `get_recommendations` | Returns analyst recommendation trends over time | `ticker` (str) | - |
| `get_upgrades_downgrades` | Returns recent rating changes (upgrades/downgrades/initiations) | `ticker`, `limit?` | 50 |
| `get_correlation` | Returns Pearson correlation of returns between two tickers | `ticker1`, `ticker2`, `period?`, `interval?` | `1y`, `1d` |
| `get_beta` | Returns beta, alpha, R-squared vs benchmark (default SPY) | `ticker`, `benchmark?`, `period?`, `interval?` | `SPY`, `1y`, `1d` |
| `get_index_constituents` | Returns index constituents with weights/sectors | `symbol` (str) | - |
| `list_available_indexes` | Lists all available indexes with metadata | - | - |
| `register_index` | Registers new index metadata for future CSV files | `symbol`, `name`, `description?`, `currency?`, `last_updated?` | `USD` |

## Available resources

| URI Template | Description | Parameters |
| :--- | :--- | :--- |
| `history://{ticker}/csv{?period,interval}` | Historical OHLCV as CSV | `ticker`, `period=1y`, `interval=1d` |
| `index://{symbol}/constituents{?format}` | Index constituents as JSON or CSV | `symbol`, `format=json` |
| `index://{symbol}/constituents.csv` | Raw CSV file content | `symbol` |
| `index://list` | List all available indexes | - |

## Available prompts

| Prompt Name | Description | Parameters | Defaults |
| :--- | :--- | :--- | :--- |
| `ask_about_stock_price` | Generates a message asking about a stock price | `company` (str) | - |
| `ask_about_top_holdings` | Generates a message asking about ETF top holdings | `fund` (str) | - |
| `ask_about_etf_equity_stats` | Generates a message asking about ETF equity valuation stats | `ticker` (str) | - |
| `ask_about_company_info` | Generates a message asking about company information | `ticker` (str) | - |
| `ask_about_company_news` | Generates a message asking about latest company news | `ticker` (str) | - |
| `ask_about_dividend_details` | Generates a message asking about dividend details | `ticker` (str) | - |
| `ask_current_date` | Generates a message asking for the current date | `fmt` (str) | `%Y-%m-%d` |
| `ask_current_time` | Generates a message asking for the current time | `fmt` (str) | `%H:%M` |

## Examples

```bash
# Run date/time example client
uv run python examples/date_time_client.py

# Run beta analysis example client
uv run python examples/beta_client.py AAPL
uv run python examples/beta_client.py TSLA SPY 5y 1wk
```

## Index Data

Index constituent data is loaded from CSV files in the `data/` directory. Available indexes:
- NDX (NASDAQ 100)
- SPX (S&P 500)
- WIG20, MWIG40, SWIG80 (Warsaw Stock Exchange)

Add new indexes by dropping CSV files in `data/` and optionally registering metadata via `register_index`.