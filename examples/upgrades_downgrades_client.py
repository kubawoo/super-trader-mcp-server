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
        changes = await client.call_tool("get_upgrades_downgrades", {"ticker": "AAPL", "limit": 10})
        c = get_data(changes)
        print(f"Upgrades/Downgrades for {c.ticker} (showing {c.count} recent)")
        for ch in c.upgrades_downgrades:
            pt = f"${ch.price_target:.2f}" if ch.price_target else "N/A"
            ppt = f"${ch.prior_price_target:.2f}" if ch.prior_price_target else "N/A"
            print(f"  {ch.date[:10]} | {ch.firm:20s} | {ch.action:12s} | {ch.from_grade or 'N/A':>10s} → {ch.to_grade or 'N/A':<10s} | Target: {pt} (was {ppt})")


if __name__ == "__main__":
    asyncio.run(main())