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
        # First get available expirations
        expirations = await client.call_tool("get_option_expirations", {"ticker": "AAPL"})
        e = get_data(expirations)
        if not e.expirations:
            print("No options available for AAPL")
            return
        
        exp_date = e.expirations[0]
        print(f"Using expiration: {exp_date}")
        
        # Get options within a strike range around current price
        # First get current price to know the range
        price_result = await client.call_tool("get_current_stock_price", {"ticker": "AAPL"})
        current_price = get_data(price_result)
        
        min_strike = round(current_price * 0.95, 2)
        max_strike = round(current_price * 1.05, 2)
        
        print(f"Current price: ${current_price:.2f}")
        print(f"Strike range: ${min_strike:.2f} - ${max_strike:.2f}")
        
        chain = await client.call_tool(
            "get_options_by_strike_range",
            {"ticker": "AAPL", "expiration_date": exp_date, "min_strike": min_strike, "max_strike": max_strike}
        )
        c = get_data(chain)
        print(f"\nOption Chain for {c.ticker} expiring {c.expiration_date} (strike range ${min_strike}-${max_strike})")
        print(f"  Underlying Price: ${c.underlying_price:.2f}")
        print(f"  Calls: {len(c.calls)} contracts")
        print(f"  Puts: {len(c.puts)} contracts")
        
        print("\n  Calls:")
        for call in c.calls:
            print(f"    Strike: ${call.strike:.2f} | Bid: {call.bid:.2f} | Ask: {call.ask:.2f} | Vol: {call.volume} | OI: {call.open_interest} | IV: {call.implied_volatility:.2%}")
        
        print("\n  Puts:")
        for put in c.puts:
            print(f"    Strike: ${put.strike:.2f} | Bid: {put.bid:.2f} | Ask: {put.ask:.2f} | Vol: {put.volume} | OI: {put.open_interest} | IV: {put.implied_volatility:.2%}")


if __name__ == "__main__":
    asyncio.run(main())