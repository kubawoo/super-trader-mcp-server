import asyncio
import sys

from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport


async def main():
    # Default ticker is AAPL, can pass as command line arg
    ticker = sys.argv[1] if len(sys.argv) > 1 else "AAPL"
    benchmark = sys.argv[2] if len(sys.argv) > 2 else "SPY"
    period = sys.argv[3] if len(sys.argv) > 3 else "1y"
    interval = sys.argv[4] if len(sys.argv) > 4 else "1d"

    transport = StreamableHttpTransport(url="http://localhost:8000/mcp")
    client = Client(transport)

    async with client:
        result = await client.call_tool(
            "get_beta",
            {
                "ticker": ticker,
                "benchmark": benchmark,
                "period": period,
                "interval": interval,
            },
        )

        beta_data = result.data

        if beta_data.error:
            print(f"Error: {beta_data.error}")
            return

        print(f"Beta Analysis: {beta_data.ticker} vs {beta_data.benchmark}")
        print(f"Period: {beta_data.period}, Interval: {beta_data.interval}")
        print(f"Data points: {beta_data.data_points}")
        print()
        print(f"  Beta (β):          {beta_data.beta:.4f}")
        print(f"  Alpha (α, annual): {beta_data.alpha:.4%}")
        print(f"  R-squared (R²):    {beta_data.r_squared:.4f}")
        print()
        print("Returns Statistics:")
        print(f"  {beta_data.ticker:>8}  Mean: {beta_data.ticker_returns_mean:.6f}  Std: {beta_data.ticker_returns_std:.6f}")
        print(f"  {beta_data.benchmark:>8}  Mean: {beta_data.benchmark_returns_mean:.6f}  Std: {beta_data.benchmark_returns_std:.6f}")
        print()
        print("Interpretation:")
        if beta_data.beta is not None:
            if beta_data.beta > 1.2:
                print(f"  {beta_data.ticker} is HIGHLY volatile vs {beta_data.benchmark} (β > 1.2)")
            elif beta_data.beta > 1.0:
                print(f"  {beta_data.ticker} is MORE volatile than {beta_data.benchmark} (β > 1.0)")
            elif beta_data.beta > 0.8:
                print(f"  {beta_data.ticker} has SIMILAR volatility to {beta_data.benchmark} (β ≈ 1.0)")
            elif beta_data.beta > 0:
                print(f"  {beta_data.ticker} is LESS volatile than {beta_data.benchmark} (β < 1.0)")
            else:
                print(f"  {beta_data.ticker} moves INVERSELY to {beta_data.benchmark} (β < 0)")


if __name__ == "__main__":
    asyncio.run(main())