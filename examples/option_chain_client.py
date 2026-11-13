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
        
        # Use the nearest expiration
        exp_date = e.expirations[0]
        print(f"Using expiration: {exp_date}")
        
        chain = await client.call_tool("get_option_chain", {"ticker": "AAPL", "expiration_date": exp_date})
        c = get_data(chain)
        print(f"Option Chain for {c.ticker} expiring {c.expiration_date}")
        print(f"  Underlying Price: ${c.underlying_price:.2f}")
        print(f"  Calls: {len(c.calls)} contracts")
        print(f"  Puts: {len(c.puts)} contracts")
        
        print("\n  Sample Calls (near ATM):")
        for call in c.calls[:5]:
            print(f"    Strike: ${call.strike:.2f} | Bid: {call.bid:.2f} | Ask: {call.ask:.2f} | Vol: {call.volume} | OI: {call.open_interest} | IV: {call.implied_volatility:.2%}")
        
        print("\n  Sample Puts (near ATM):")
        for put in c.puts[:5]:
            print(f"    Strike: ${put.strike:.2f} | Bid: {put.bid:.2f} | Ask: {put.ask:.2f} | Vol: {put.volume} | OI: {put.open_interest} | IV: {put.implied_volatility:.2%}")


if __name__ == "__main__":
    asyncio.run(main())