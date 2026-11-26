import asyncio

from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport


def get_data(result):
    """Extract data from CallToolResult, handling RootModel wrapper."""
    data = result.data
    if hasattr(data, "root"):
        return data.root
    return data


async def main():
    transport = StreamableHttpTransport(url="http://localhost:8000/mcp")
    client = Client(transport)
    async with client:
        # Example 1: Daily data for 1 month
        print("=== AAPL Daily Prices (1 month) ===")
        result = await client.call_tool(
            "get_historical_quotes", {"ticker": "AAPL", "period": "1mo", "interval": "1d"}
        )
        data = get_data(result)
        
        print(f"Ticker: {data.ticker} | Period: {data.period} | Interval: {data.interval} | Count: {data.count}")
        print()
        print(f"{'Date':<12} {'Open':>10} {'High':>10} {'Low':>10} {'Close':>10} {'Volume':>12}")
        print("-" * 60)
        for q in data.quotes:
            print(
                f"{q.date:<12} "
                f"${q.open:>9.2f} "
                f"${q.high:>9.2f} "
                f"${q.low:>9.2f} "
                f"${q.close:>9.2f} "
                f"{q.volume:>12,}"
            )
        print()

        # Example 2: Hourly data for 1 week (intraday)
        print("=== SPY Hourly Prices (1 week) ===")
        result = await client.call_tool(
            "get_historical_quotes", {"ticker": "SPY", "period": "1wk", "interval": "1h"}
        )
        data = get_data(result)
        
        print(f"Ticker: {data.ticker} | Period: {data.period} | Interval: {data.interval} | Count: {data.count}")
        print()
        print(f"{'DateTime':<20} {'Open':>10} {'High':>10} {'Low':>10} {'Close':>10} {'Volume':>12}")
        print("-" * 70)
        for q in data.quotes[:20]:  # Show first 20 bars
            print(
                f"{q.date:<20} "
                f"${q.open:>9.2f} "
                f"${q.high:>9.2f} "
                f"${q.low:>9.2f} "
                f"${q.close:>9.2f} "
                f"{q.volume:>12,}"
            )
        if data.count > 20:
            print(f"... and {data.count - 20} more rows")
        print()

        # Example 3: Weekly data for 1 year
        print("=== TSLA Weekly Prices (1 year) ===")
        result = await client.call_tool(
            "get_historical_quotes", {"ticker": "TSLA", "period": "1y", "interval": "1wk"}
        )
        data = get_data(result)
        
        print(f"Ticker: {data.ticker} | Period: {data.period} | Interval: {data.interval} | Count: {data.count}")
        print()
        print(f"{'Date':<12} {'Open':>10} {'High':>10} {'Low':>10} {'Close':>10} {'Volume':>12}")
        print("-" * 60)
        for q in data.quotes:
            print(
                f"{q.date:<12} "
                f"${q.open:>9.2f} "
                f"${q.high:>9.2f} "
                f"${q.low:>9.2f} "
                f"${q.close:>9.2f} "
                f"{q.volume:>12,}"
            )


if __name__ == "__main__":
    asyncio.run(main())