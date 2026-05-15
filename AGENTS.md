# super-trader-mcp-server

Python 3.13+ MCP server for traders built on [`fastmcp`](https://github.com/jlowin/fastmcp).

## Quick start

```bash
uv run super-trader-mcp-server   # starts on :8000 (or $FASTMCP_PORT)
curl http://localhost:8000/health # → OK
```

## Commands

| Action | Command |
|---|---|
| Run server | `uv run super-trader-mcp-server` |
| Run example client | `uv run python examples/date_time_client.py` |
| Update deps | `./update_deps.sh` (runs `uv sync --upgrade && uv lock && uv audit`) |

## Project structure

```
src/super_trader_mcp_server/
├── main.py       # entrypoint → calls start_server()
├── mcpserver.py  # FastMCP app, health check, CORS, start_server()
├── models.py     # TopHoldingModel, ETFEquityStatsModel, StockInfoModel (pydantic)
├── resources/
│   └── trading.py  # get_history_csv resource template
├── tools/
│   ├── trading.py  # get_current_stock_price, get_top_holdings, get_etf_equity_stats, get_company_info
│   └── utils.py    # get_current_time, get_current_date
└── prompts/
    ├── trading.py  # ask_about_stock_price, ask_about_top_holdings, ask_about_etf_equity_stats, ask_about_company_info
    └── utils.py    # ask_current_date, ask_current_time
```

## Key details

- **Transport**: HTTP only (`mcp.run(transport="http")`), **not** stdio. The MCP endpoint is at `/mcp` via SSE/streamable HTTP.
- **Port**: `FASTMCP_PORT` env var (default `8000`). `.env` in repo sets `8001` + disables update checks/banner.
- **Tools use `yfinance`** — no API key needed, but depends on Yahoo Finance availability.
- **No tests, no CI, no linter config, no typechecker config** in the repo.
- **Bruno collection** at `bruno/` for manual API testing (uses `mcp-session-id` header from init response).
- **Build**: `uv_build` backend, package name `super-trader-mcp-server`.

## Patterns

- Tools/prompts/resources auto-register via `@mcp.tool` / `@mcp.prompt` / `@mcp.resource` decorators on import. Registration is triggered by `register_*()` in each directory's `__init__.py`.
- All tools are `async`.
- New tools go in `tools/` with an import added to `tools/__init__.py`'s `register_tools()`. Same pattern for `resources/` and `prompts/`.
- Custom HTTP routes use `@mcp.custom_route` (see `/health` in `mcpserver.py`).
- Resource templates use `{param}` in the URI (RFC 6570). The `history://{ticker}/csv{?period,interval}` resource is available at `history://<TICKER>/csv?period=<PERIOD>&interval=<INTERVAL>`.
