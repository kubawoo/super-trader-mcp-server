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
        holdings = await client.call_tool("get_top_holdings", {"ticker": "SPY"})
        data = get_data(holdings)
        print(f"SPY Top Holdings ({len(data)} items):")
        for h in data:
            print(f"  {h.ticker:6} {h.name:30} {h.pct:.2f}%")


if __name__ == "__main__":
    asyncio.run(main())