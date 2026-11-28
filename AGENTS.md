# super-trader-mcp-server

Python 3.13+ MCP server for traders built on [`fastmcp`](https://github.com/jlowin/fastmcp).

## Quick start

```bash
uv run super-trader   # starts on :8000 (or $FASTMCP_PORT)
curl http://localhost:8000/health # → OK
```

## Commands

| Action | Command |
|---|---|
| Run server | `uv run super-trader` |
| Run example client | `uv run python examples/date_time_client.py` |
| Run beta example | `uv run python examples/beta_client.py AAPL` |
| Update deps | `./update_deps.sh` (runs `uv sync --upgrade && uv lock && uv audit`) |

## Project structure

```
src/super_trader/
├── main.py              # entrypoint → calls start_server()
├── mcpserver.py         # FastMCP app, health check, CORS, start_server()
├── models.py            # All Pydantic models (stock, ETF, options, earnings, analyst, index, financial statements, historical quotes, correlation, beta)
├── utils/
│   └── index_data.py    # Generic CSV-based index constituent loader
├── resources/
│   ├── __init__.py      # register_resources()
│   ├── trading.py       # get_history_csv resource template
│   └── indexes.py       # index:// resources (constituents JSON/CSV, list)
├── tools/
│   ├── __init__.py      # register_tools()
│   ├── trading.py       # Core trading tools (22 tools)
│   ├── indexes.py       # Index constituent tools
│   └── utils.py         # get_current_time, get_current_date
└── prompts/
    ├── __init__.py      # register_prompts()
    ├── trading.py       # Trading-related prompts (7 prompts)
    └── utils.py         # Time/date prompts
```

## Key details

- **Transport**: HTTP only (`mcp.run(transport="http")`), **not** stdio. The MCP endpoint is at `/mcp` via SSE/streamable HTTP.
- **Port**: `FASTMCP_PORT` env var (default `8000`). `.env` in repo sets `8001` + disables update checks/banner.
- **Tools use `yfinance`** — no API key needed, but depends on Yahoo Finance availability.
- **Package name**: `super-trader` (entrypoint: `super-trader`), Python package: `super_trader`
- **No tests, no CI, no linter config, no typechecker config** in the repo.
- **Bruno collection** at `bruno/` for manual API testing (uses `mcp-session-id` header from init response).
- **Build**: `uv_build` backend.
- **Index data**: CSV files in `data/` directory (e.g., `nasdaq100.csv`, `sp500.csv`, `wig20.csv`, etc.)

## Tools (22 tools in `tools/trading.py`)

### Stock/ETF Basics
- `get_current_stock_price(ticker)` — Real-time price with pre/post market
- `get_company_info(ticker)` — Profile, financials, valuation, dividends
- `get_company_news(ticker)` — Latest news articles
- `get_dividend_details(ticker)` — Full dividend history + metrics
- `get_historical_quotes(ticker, period, interval)` — OHLCV bars (CSV also available via resource)

### ETF/Fund Analysis
- `get_top_holdings(ticker)` — Top portfolio holdings
- `get_etf_equity_stats(ticker)` — Valuation metrics vs category average

### Financial Statements
- `get_income_statement(ticker, quarterly, ttm)` — Annual/quarterly/TTM
- `get_balance_sheet(ticker, quarterly)` — Annual/quarterly
- `get_cash_flow(ticker, quarterly, ttm)` — Annual/quarterly/TTM

### Options
- `get_option_expirations(ticker)` — Available expiration dates
- `get_option_chain(ticker, expiration_date)` — Full call/put chain
- `get_atm_options(ticker, expiration_date?, nearby_strikes?)` — ATM + nearby strikes
- `get_options_by_strike_range(ticker, expiration_date, min_strike?, max_strike?)` — Filtered chain

### Earnings
- `get_earnings_dates(ticker)` — Upcoming + historical dates with estimates/surprises
- `get_earnings_history(ticker)` — Quarterly actuals vs estimates
- `get_earnings_estimates(ticker)` — Current/next quarter & year analyst estimates

### Analyst Data
- `get_analyst_price_targets(ticker)` — High/low/mean/median/current
- `get_recommendations(ticker)` — Rating trends over time
- `get_upgrades_downgrades(ticker, limit?)` — Recent rating changes

### Correlation
- `get_correlation(ticker1, ticker2, period?, interval?)` — Pearson correlation of returns

### Beta
- `get_beta(ticker, benchmark?, period?, interval?)` — Beta vs benchmark (default: SPY) with alpha and R-squared

### Indexes (`tools/indexes.py`)
- `get_index_constituents(symbol)` — Constituents with weights/sectors
- `list_available_indexes()` — All registered indexes
- `register_index(symbol, name, ...)` — Register new index metadata

### Utils (`tools/utils.py`)
- `get_current_date(fmt?)`
- `get_current_time(fmt?)`

## Resources

- `history://{ticker}/csv{?period,interval}` — Historical OHLCV as CSV
- `index://{symbol}/constituents{?format}` — Index constituents (JSON or CSV)
- `index://{symbol}/constituents.csv` — Raw CSV file content
- `index://list` — List all available indexes

## Prompts

### Trading (`prompts/trading.py`)
- `ask_about_stock_price(company)`
- `ask_about_top_holdings(fund)`
- `ask_about_etf_equity_stats(ticker)`
- `ask_about_company_info(ticker)`
- `ask_about_company_news(ticker)`
- `ask_about_dividend_details(ticker)`

### Utils (`prompts/utils.py`)
- `ask_current_date(fmt?)`
- `ask_current_time(fmt?)`

## Patterns

- Tools/prompts/resources auto-register via `@mcp.tool` / `@mcp.prompt` / `@mcp.resource` decorators on import. Registration is triggered by `register_*()` in each directory's `__init__.py`.
- All tools are `async`.
- New tools go in `tools/` with an import added to `tools/__init__.py`'s `register_tools()`. Same pattern for `resources/` and `prompts/`.
- Custom HTTP routes use `@mcp.custom_route` (see `/health` in `mcpserver.py`).
- Resource templates use `{param}` in the URI (RFC 6570). The `history://{ticker}/csv{?period,interval}` resource is available at `history://<TICKER>/csv?period=<PERIOD>&interval=<INTERVAL>`.
- Index data loaded from CSV files in `data/` directory via `utils/index_data.py`. Add new indexes by dropping CSV files and optionally registering metadata.