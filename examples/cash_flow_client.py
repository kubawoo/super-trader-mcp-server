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
        # Annual cash flow
        annual = await client.call_tool("get_cash_flow", {"ticker": "AAPL"})
        a = get_data(annual)
        print(f"Cash Flow for {a.ticker} ({a.frequency})")
        for p in a.periods[:3]:
            print(f"  Period ending {p.period_end}:")
            print(f"    Operating Cash Flow: ${p.operating_cash_flow:,.0f}")
            print(f"    Capital Expenditure: ${p.capital_expenditure:,.0f}")
            print(f"    Free Cash Flow: ${p.free_cash_flow:,.0f}")
            print(f"    Dividends Paid: ${p.cash_dividends_paid:,.0f}")
            print(f"    Share Repurchases: ${p.repurchase_of_capital_stock:,.0f}")

        print("\n--- Quarterly ---")
        quarterly = await client.call_tool("get_cash_flow", {"ticker": "AAPL", "quarterly": True})
        q = get_data(quarterly)
        for p in q.periods[:3]:
            print(f"  Period ending {p.period_end}:")
            print(f"    Operating Cash Flow: ${p.operating_cash_flow:,.0f}")
            print(f"    Free Cash Flow: ${p.free_cash_flow:,.0f}")

        print("\n--- TTM ---")
        ttm = await client.call_tool("get_cash_flow", {"ticker": "AAPL", "ttm": True})
        t = get_data(ttm)
        for p in t.periods:
            print(f"  Period ending {p.period_end}:")
            print(f"    Operating Cash Flow: ${p.operating_cash_flow:,.0f}")
            print(f"    Free Cash Flow: ${p.free_cash_flow:,.0f}")


if __name__ == "__main__":
    asyncio.run(main())