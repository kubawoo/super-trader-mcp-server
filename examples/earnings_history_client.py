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
        history = await client.call_tool("get_earnings_history", {"ticker": "AAPL"})
        h = get_data(history)
        print(f"Earnings History for {h.ticker} ({h.count} quarters)")
        for item in h.history:
            act = f"${item.eps_actual:.2f}" if item.eps_actual else "N/A"
            est = f"${item.eps_estimate:.2f}" if item.eps_estimate else "N/A"
            diff = f"${item.eps_difference:.2f}" if item.eps_difference else "N/A"
            surp = f"{item.surprise_percent*100:.1f}%" if item.surprise_percent else "N/A"
            print(f"  {item.quarter}: Actual={act}, Estimate={est}, Diff={diff}, Surprise={surp} ({item.methodology})")


if __name__ == "__main__":
    asyncio.run(main())