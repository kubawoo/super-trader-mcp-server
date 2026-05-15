import yfinance as yf

from super_trader_mcp_server.mcpserver import mcp


@mcp.resource(
    "history://{ticker}/csv{?period,interval}",
    mime_type="text/csv",
    description="Historical OHLCV prices for a ticker as CSV",
)
async def get_history_csv(ticker: str = "", period: str = "1y", interval: str = "1d") -> str:
    stk = yf.Ticker(ticker)
    hist = stk.history(period=period, interval=interval)
    return hist.to_csv()
