# super-trader-mcp-server

![Version](https://img.shields.io/github/v/release/kubawoo/super-trader-mcp-server?style=flat-square)
![License](https://img.shields.io/github/license/kubawoo/super-trader-mcp-server?style=flat-square)
![Python](https://img.shields.io/badge/python-3.13%2B-blue?style=flat-square)

MCP Server offering a set of tools for traders and investors.

## Features

- **Real-time Stock/ETF Prices**: Get current market prices using `yfinance`.
- **ETF Insights**: Retrieve top holdings and equity valuation metrics (P/E, P/B, etc.) for ETFs.
- **Company Info**: Look up sector, industry, market cap, and employee count.
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
uv run super-trader-mcp-server

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
| `get_current_stock_price` | Returns the current price of a stock or ETF | `ticker` (str) | - |
| `get_top_holdings` | Returns the top 10 holdings of an ETF | `ticker` (str) | - |
| `get_etf_equity_stats` | Returns equity valuation metrics (P/E, P/B, P/S, P/CF) for an ETF | `ticker` (str) | - |
| `get_company_info` | Returns basic company information like sector, industry, and market cap | `ticker` (str) | - |

## Available prompts

| Prompt Name | Description | Parameters | Defaults |
| :--- | :--- | :--- | :--- |
| `ask_about_stock_price` | Generates a message asking about a stock price | `company` (str) | - |
| `ask_about_top_holdings` | Generates a message asking about ETF top holdings | `fund` (str) | - |
| `ask_about_etf_equity_stats` | Generates a message asking about ETF equity valuation stats | `ticker` (str) | - |
| `ask_about_company_info` | Generates a message asking about company information | `ticker` (str) | - |
| `ask_current_date` | Generates a message asking for the current date | `fmt` (str) | `%Y-%m-%d` |
| `ask_current_time` | Generates a message asking for the current time | `fmt` (str) | `%H:%M` |
