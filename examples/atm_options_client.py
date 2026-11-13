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
        # Get ATM options for nearest expiration
        atm = await client.call_tool("get_atm_options", {"ticker": "AAPL", "nearby_strikes": 3})
        a = get_data(atm)
        print(f"ATM Options for {a.ticker} expiring {a.expiration_date}")
        print(f"  Underlying Price: ${a.underlying_price:.2f}")
        print(f"  ATM Strike: ${a.atm_strike:.2f}")
        
        if a.call:
            c = a.call
            print(f"\n  ATM Call (${a.atm_strike}):")
            print(f"    Bid: {c.bid:.2f} | Ask: {c.ask:.2f} | Last: {c.last_price:.2f}")
            print(f"    Volume: {c.volume} | OI: {c.open_interest} | IV: {c.implied_volatility:.2%}")
            print(f"    ITM: {c.in_the_money}")
        
        if a.put:
            p = a.put
            print(f"\n  ATM Put (${a.atm_strike}):")
            print(f"    Bid: {p.bid:.2f} | Ask: {p.ask:.2f} | Last: {p.last_price:.2f}")
            print(f"    Volume: {p.volume} | OI: {p.open_interest} | IV: {p.implied_volatility:.2%}")
            print(f"    ITM: {p.in_the_money}")
        
        print(f"\n  Nearby Calls ({len(a.nearby_calls)} contracts):")
        for c in a.nearby_calls:
            print(f"    Strike: ${c.strike:.2f} | Bid: {c.bid:.2f} | Ask: {c.ask:.2f} | IV: {c.implied_volatility:.2%}")
        
        print(f"\n  Nearby Puts ({len(a.nearby_puts)} contracts):")
        for p in a.nearby_puts:
            print(f"    Strike: ${p.strike:.2f} | Bid: {p.bid:.2f} | Ask: {p.ask:.2f} | IV: {p.implied_volatility:.2%}")


if __name__ == "__main__":
    asyncio.run(main())