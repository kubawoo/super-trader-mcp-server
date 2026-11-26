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
        targets = await client.call_tool("get_analyst_price_targets", {"ticker": "AAPL"})
        t = get_data(targets)
        pt = t.price_targets
        print(f"Analyst Price Targets for {t.ticker}")
        print(f"  Current Price: ${pt.current:.2f}" if pt.current else "  Current Price: N/A")
        print(f"  High Target:   ${pt.high:.2f}" if pt.high else "  High Target:   N/A")
        print(f"  Low Target:    ${pt.low:.2f}" if pt.low else "  Low Target:    N/A")
        print(f"  Mean Target:   ${pt.mean:.2f}" if pt.mean else "  Mean Target:   N/A")
        print(f"  Median Target: ${pt.median:.2f}" if pt.median else "  Median Target: N/A")


if __name__ == "__main__":
    asyncio.run(main())