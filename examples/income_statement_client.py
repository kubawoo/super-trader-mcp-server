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
        # Annual income statement
        annual = await client.call_tool("get_income_statement", {"ticker": "AAPL"})
        a = get_data(annual)
        print(f"Income Statement for {a.ticker} ({a.frequency})")
        for p in a.periods[:3]:
            print(f"  Period ending {p.period_end}:")
            print(f"    Revenue: ${p.total_revenue:,.0f}")
            print(f"    Gross Profit: ${p.gross_profit:,.0f}")
            print(f"    Operating Income: ${p.operating_income:,.0f}")
            print(f"    Net Income: ${p.net_income:,.0f}")
            print(f"    Diluted EPS: ${p.diluted_eps:.2f}")

        print("\n--- Quarterly ---")
        quarterly = await client.call_tool("get_income_statement", {"ticker": "AAPL", "quarterly": True})
        q = get_data(quarterly)
        for p in q.periods[:3]:
            print(f"  Period ending {p.period_end}:")
            print(f"    Revenue: ${p.total_revenue:,.0f}")
            print(f"    Net Income: ${p.net_income:,.0f}")

        print("\n--- TTM ---")
        ttm = await client.call_tool("get_income_statement", {"ticker": "AAPL", "ttm": True})
        t = get_data(ttm)
        for p in t.periods:
            print(f"  Period ending {p.period_end}:")
            print(f"    Revenue: ${p.total_revenue:,.0f}")
            print(f"    Net Income: ${p.net_income:,.0f}")


if __name__ == "__main__":
    asyncio.run(main())