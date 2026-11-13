import asyncio

from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport


def get_data(result):
    """Extract data from CallToolResult, handling RootModel wrapper."""
    data = result.data
    if hasattr(data, "root"):
        return data.root
    return data


def fmt(val, fmt_str=None):
    """Format value, handling None."""
    if val is None:
        return "N/A"
    if fmt_str:
        return format(val, fmt_str)
    return str(val)


async def main():
    transport = StreamableHttpTransport(url="http://localhost:8000/mcp")
    client = Client(transport)
    async with client:
        stats = await client.call_tool("get_etf_equity_stats", {"ticker": "SPY"})
        s = get_data(stats)
        print(f"ETF Equity Stats for {s.ticker}")
        print(f"  P/E Ratio:          {fmt(s.price_earnings, '.2f')} (Category: {fmt(s.category_average_price_earnings, '.2f')})")
        print(f"  P/B Ratio:          {fmt(s.price_book, '.2f')} (Category: {fmt(s.category_average_price_book, '.2f')})")
        print(f"  P/S Ratio:          {fmt(s.price_sales, '.2f')} (Category: {fmt(s.category_average_price_sales, '.2f')})")
        print(f"  P/Cashflow Ratio:   {fmt(s.price_cashflow, '.2f')} (Category: {fmt(s.category_average_price_cashflow, '.2f')})")
        print(f"  Median Market Cap:  ${fmt(s.median_market_cap, ',.0f')} (Category: ${fmt(s.category_average_median_market_cap, ',.0f')})")
        print(f"  3Y Earnings Growth: {fmt(s.three_year_earnings_growth, '.2f')}% (Category: {fmt(s.category_average_three_year_earnings_growth, '.2f')}%)")


if __name__ == "__main__":
    asyncio.run(main())