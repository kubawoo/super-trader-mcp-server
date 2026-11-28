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
        # Example 1: Correlation between AAPL and MSFT (1 year, daily)
        print("=" * 60)
        print("Correlation: AAPL vs MSFT (1 year, daily)")
        print("=" * 60)
        result = await client.call_tool(
            "get_correlation",
            {"ticker1": "AAPL", "ticker2": "MSFT", "period": "1y", "interval": "1d"}
        )
        corr = get_data(result)
        
        if corr.error:
            print(f"Error: {corr.error}")
        else:
            print(f"Ticker 1: {corr.ticker1}")
            print(f"Ticker 2: {corr.ticker2}")
            print(f"Period:   {corr.period}")
            print(f"Interval: {corr.interval}")
            print(f"Data Points: {corr.data_points}")
            print(f"Correlation: {corr.correlation:.4f}" if corr.correlation else "Correlation: N/A")
            print()
            print(f"{corr.ticker1} Returns - Mean: {corr.ticker1_returns_mean:.6f}, Std: {corr.ticker1_returns_std:.6f}" if corr.ticker1_returns_mean is not None else f"{corr.ticker1} Returns: N/A")
            print(f"{corr.ticker2} Returns - Mean: {corr.ticker2_returns_mean:.6f}, Std: {corr.ticker2_returns_std:.6f}" if corr.ticker2_returns_mean is not None else f"{corr.ticker2} Returns: N/A")
            print()
            
            # Interpret correlation
            if corr.correlation is not None:
                if corr.correlation > 0.7:
                    strength = "Strong positive"
                elif corr.correlation > 0.3:
                    strength = "Moderate positive"
                elif corr.correlation > -0.3:
                    strength = "Weak/No correlation"
                elif corr.correlation > -0.7:
                    strength = "Moderate negative"
                else:
                    strength = "Strong negative"
                print(f"Interpretation: {strength} correlation ({corr.correlation:.2f})")
        
        print()
        
        # Example 2: Correlation between SPY and QQQ (6 months, daily)
        print("=" * 60)
        print("Correlation: SPY vs QQQ (6 months, daily)")
        print("=" * 60)
        result = await client.call_tool(
            "get_correlation",
            {"ticker1": "SPY", "ticker2": "QQQ", "period": "6mo", "interval": "1d"}
        )
        corr = get_data(result)
        
        if corr.error:
            print(f"Error: {corr.error}")
        else:
            print(f"Correlation: {corr.correlation:.4f}" if corr.correlation else "Correlation: N/A")
            print(f"Data Points: {corr.data_points}")
            if corr.correlation is not None:
                if corr.correlation > 0.7:
                    strength = "Strong positive"
                elif corr.correlation > 0.3:
                    strength = "Moderate positive"
                elif corr.correlation > -0.3:
                    strength = "Weak/No correlation"
                elif corr.correlation > -0.7:
                    strength = "Moderate negative"
                else:
                    strength = "Strong negative"
                print(f"Interpretation: {strength} correlation ({corr.correlation:.2f})")
        
        print()
        
        # Example 3: Correlation between AAPL and TSLA (3 months, daily)
        print("=" * 60)
        print("Correlation: AAPL vs TSLA (3 months, daily)")
        print("=" * 60)
        result = await client.call_tool(
            "get_correlation",
            {"ticker1": "AAPL", "ticker2": "TSLA", "period": "3mo", "interval": "1d"}
        )
        corr = get_data(result)
        
        if corr.error:
            print(f"Error: {corr.error}")
        else:
            print(f"Correlation: {corr.correlation:.4f}" if corr.correlation else "Correlation: N/A")
            print(f"Data Points: {corr.data_points}")
            if corr.correlation is not None:
                if corr.correlation > 0.7:
                    strength = "Strong positive"
                elif corr.correlation > 0.3:
                    strength = "Moderate positive"
                elif corr.correlation > -0.3:
                    strength = "Weak/No correlation"
                elif corr.correlation > -0.7:
                    strength = "Moderate negative"
                else:
                    strength = "Strong negative"
                print(f"Interpretation: {strength} correlation ({corr.correlation:.2f})")


if __name__ == "__main__":
    asyncio.run(main())