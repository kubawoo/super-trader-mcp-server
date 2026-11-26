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
        earnings = await client.call_tool("get_earnings_dates", {"ticker": "AAPL"})
        e = get_data(earnings)
        print(f"Earnings Dates for {e.ticker} ({e.count} entries)")
        for ed in e.earnings_dates:
            est = f"${ed.eps_estimate:.2f}" if ed.eps_estimate else "N/A"
            rep = f"${ed.reported_eps:.2f}" if ed.reported_eps else "N/A"
            surp = f"{ed.surprise_percent:.1f}%" if ed.surprise_percent else "N/A"
            print(f"  {ed.earnings_date}: Est={est}, Reported={rep}, Surprise={surp}")


if __name__ == "__main__":
    asyncio.run(main())