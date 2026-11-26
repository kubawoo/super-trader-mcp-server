import asyncio
from datetime import datetime

from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport


def get_data(result):
    """Extract data from CallToolResult, handling RootModel wrapper."""
    data = result.data
    if hasattr(data, "root"):
        return data.root
    return data


def fmt_time(ts: int | None) -> str:
    if ts is None:
        return "N/A"
    return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")


async def main():
    transport = StreamableHttpTransport(url="http://localhost:8000/mcp")
    client = Client(transport)
    async with client:
        result = await client.call_tool("get_current_stock_price", {"ticker": "AAPL"})
        price = get_data(result)
        
        print(f"Stock Price for {price.ticker} ({price.currency}) - Market State: {price.market_state}")
        print()
        
        # Regular market
        print("Regular Market (9:30 AM - 4:00 PM ET):")
        print(f"  Price:       ${price.regular_market_price:.2f}" if price.regular_market_price else "  Price:       N/A")
        print(f"  Change:      {price.regular_market_change:+.2f}" if price.regular_market_change is not None else "  Change:      N/A")
        print(f"  Change %:    {price.regular_market_change_percent:+.2f}%" if price.regular_market_change_percent is not None else "  Change %:    N/A")
        print(f"  Time:        {fmt_time(price.regular_market_time)}")
        print()
        
        # Pre-market
        print("Pre-Market (4:00 AM - 9:30 AM ET):")
        print(f"  Price:       ${price.pre_market_price:.2f}" if price.pre_market_price else "  Price:       N/A")
        print(f"  Change:      {price.pre_market_change:+.2f}" if price.pre_market_change is not None else "  Change:      N/A")
        print(f"  Change %:    {price.pre_market_change_percent:+.2f}%" if price.pre_market_change_percent is not None else "  Change %:    N/A")
        print(f"  Time:        {fmt_time(price.pre_market_time)}")
        print()
        
        # Post-market
        print("Post-Market (4:00 PM - 8:00 PM ET):")
        print(f"  Price:       ${price.post_market_price:.2f}" if price.post_market_price else "  Price:       N/A")
        print(f"  Change:      {price.post_market_change:+.2f}" if price.post_market_change is not None else "  Change:      N/A")
        print(f"  Change %:    {price.post_market_change_percent:+.2f}%" if price.post_market_change_percent is not None else "  Change %:    N/A")
        print(f"  Time:        {fmt_time(price.post_market_time)}")


if __name__ == "__main__":
    asyncio.run(main())