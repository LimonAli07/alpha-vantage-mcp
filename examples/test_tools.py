#!/usr/bin/env python3
"""
Simple test script to verify new tool integration
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the parent directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.alpha_vantage_mcp.server import handle_list_tools

async def test_tools_list():
    """Test that new tools are properly registered"""
    os.environ["ALPHA_VANTAGE_API_KEY"] = "test_key"
    
    tools = await handle_list_tools()
    
    # Expected new tools
    expected_tools = [
        "get-stock-quote",
        "get-company-info", 
        "get-crypto-exchange-rate",
        "get-time-series",
        "get-historical-options",
        "get-crypto-daily",
        "get-crypto-weekly", 
        "get-crypto-monthly",
        "get-yahoo-quote",
        "get-eodhd-fundamentals",
        "get-insider-transactions",
        "get-company-news",
        "get-market-news",
        "get-reddit-sentiment",
        "get-twitter-sentiment"
    ]
    
    tool_names = [tool.name for tool in tools]
    
    print(f"Total tools registered: {len(tools)}")
    print(f"Expected tools: {len(expected_tools)}")
    
    missing_tools = [tool for tool in expected_tools if tool not in tool_names]
    extra_tools = [tool for tool in tool_names if tool not in expected_tools]
    
    if missing_tools:
        print(f"Missing tools: {missing_tools}")
    if extra_tools:
        print(f"Extra tools: {extra_tools}")
    
    if len(tools) == len(expected_tools) and not missing_tools:
        print("✅ All tools registered successfully!")
        return True
    else:
        print("❌ Tool registration mismatch")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_tools_list())
    exit(0 if success else 1)