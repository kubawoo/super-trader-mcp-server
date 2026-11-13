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
        divs = await client.call_tool("get_dividend_details", {"ticker": "AAPL"})
        d = get_data(divs)
        print(f"Dividend Details for {d.ticker}")
        print(f"  Dividend Rate:            {d.dividend_rate}")
        print(f"  Dividend Yield:           {d.dividend_yield}")
        print(f"  Trailing Annual Rate:     {d.trailing_annual_dividend_rate}")
        print(f"  Trailing Annual Yield:    {d.trailing_annual_dividend_yield}")
        print(f"  Ex-Dividend Date:         {d.ex_dividend_date}")
        print(f"  Dividend Date:            {d.dividend_date}")
        print(f"  Payout Ratio:             {d.payout_ratio}")
        print(f"  5Y Avg Dividend Yield:    {d.five_year_avg_dividend_yield}")
        print(f"  History ({len(d.history)} payments):")
        for h in d.history[-5:]:
            print(f"    {h.date}: ${h.amount:.4f}")


if __name__ == "__main__":
    asyncio.run(main())