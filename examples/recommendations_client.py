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
        recs = await client.call_tool("get_recommendations", {"ticker": "AAPL"})
        r = get_data(recs)
        print(f"Analyst Recommendations for {r.ticker} ({r.count} periods)")
        print(f"  {'Period':>6}  {'Strong Buy':>10}  {'Buy':>6}  {'Hold':>6}  {'Sell':>6}  {'Strong Sell':>11}  {'Total':>6}")
        for rec in r.recommendations:
            print(f"  {rec.period:>6}  {rec.strong_buy:>10}  {rec.buy:>6}  {rec.hold:>6}  {rec.sell:>6}  {rec.strong_sell:>11}  {rec.total:>6}")


if __name__ == "__main__":
    asyncio.run(main())