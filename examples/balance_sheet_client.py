import asyncio

from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport


def get_data(result):
    """Extract data from CallToolResult, handling RootModel wrapper."""
    data = result.data
    if hasattr(data, "root"):
        return data.root
    return data


def unwrap_periods(periods):
    """Unwrap RootModel wrappers from period list items."""
    if hasattr(periods, "root"):
        periods = periods.root
    result = []
    for p in periods:
        if hasattr(p, "root"):
            result.append(p.root)
        else:
            result.append(p)
    return result


async def main():
    transport = StreamableHttpTransport(url="http://localhost:8000/mcp")
    client = Client(transport)
    async with client:
        # Annual balance sheet
        annual = await client.call_tool("get_balance_sheet", {"ticker": "AAPL"})
        a = get_data(annual)
        a.periods = unwrap_periods(a.periods)
        print(f"Balance Sheet for {a.ticker} ({a.frequency})")
        for p in a.periods[:3]:
            print(f"  Period ending {p.period_end}:")
            print(f"    Total Assets: ${p.total_assets:,.0f}")
            print(f"    Total Current Assets: ${p.total_current_assets:,.0f}")
            print(f"    Cash & Equivalents: ${p.cash_and_cash_equivalents:,.0f}")
            print(f"    Total Liabilities: ${p.total_liabilities:,.0f}")
            print(f"    Total Current Liabilities: ${p.total_current_liabilities:,.0f}")
            print(f"    Total Equity: ${p.total_equity:,.0f}")
            print(f"    Total Debt: ${p.total_debt:,.0f}")
            print(f"    Net Debt: ${p.net_debt:,.0f}")
            print(f"    Working Capital: ${p.working_capital:,.0f}")

        print("\n--- Quarterly ---")
        quarterly = await client.call_tool("get_balance_sheet", {"ticker": "AAPL", "quarterly": True})
        q = get_data(quarterly)
        q.periods = unwrap_periods(q.periods)
        for p in q.periods[:3]:
            print(f"  Period ending {p.period_end}:")
            print(f"    Total Assets: ${p.total_assets:,.0f}")
            print(f"    Total Equity: ${p.total_equity:,.0f}")
            print(f"    Total Debt: ${p.total_debt:,.0f}")
            print(f"    Net Debt: ${p.net_debt:,.0f}")


if __name__ == "__main__":
    asyncio.run(main())