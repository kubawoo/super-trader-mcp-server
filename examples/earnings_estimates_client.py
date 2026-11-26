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
        estimates = await client.call_tool("get_earnings_estimates", {"ticker": "AAPL"})
        e = get_data(estimates)
        print(f"Earnings Estimates for {e.ticker} ({e.count} periods)")
        for est in e.estimates:
            avg = f"${est.avg_estimate:.2f}" if est.avg_estimate else "N/A"
            low = f"${est.low_estimate:.2f}" if est.low_estimate else "N/A"
            high = f"${est.high_estimate:.2f}" if est.high_estimate else "N/A"
            yag = f"${est.year_ago_eps:.2f}" if est.year_ago_eps else "N/A"
            growth = f"{est.growth*100:.1f}%" if est.growth else "N/A"
            print(f"  {est.period}: Avg={avg}, Low={low}, High={high}, Year Ago={yag}, Growth={growth} ({est.currency}, {est.methodology})")


if __name__ == "__main__":
    asyncio.run(main())