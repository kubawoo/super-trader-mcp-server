from typing import List

from super_trader_mcp_server.mcpserver import mcp


@mcp.tool
async def sum_numbers(numbers: List[float]) -> float:
    """Returns the sum of numbers"""
    return sum(numbers)


@mcp.tool
async def average_numbers(numbers: List[float]) -> float:
    """Returns the average of numbers"""
    return sum(numbers) / len(numbers)
