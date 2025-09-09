# Multi-Source Financial Data MCP Server - Examples

This directory contains example configurations and usage patterns for the Multi-Source Financial Data MCP Server.

## Files

### `claude_desktop_config.json`
Example configuration for Claude Desktop that includes all the new API integrations. Copy this to your Claude Desktop configuration file and replace the placeholder values with your actual API keys and paths.

**Configuration Path:**
- **MacOS**: `~/Library/Application\ Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%/Claude/claude_desktop_config.json`

### `usage_examples.py`
Demonstration script showing how to call the various MCP tools. Note that in practice, these tools are called through the MCP protocol by clients like Claude Desktop, not directly in Python.

## Quick Start

1. **Set up API keys**: Copy `.env.sample` to `.env` and fill in your API keys:
   ```bash
   cp .env.sample .env
   # Edit .env with your API keys
   ```

2. **Configure Claude Desktop**: Update your Claude Desktop configuration with the example configuration, adjusting paths and API keys.

3. **Test the server**: You can test the server manually:
   ```bash
   # Set required API key
   export ALPHA_VANTAGE_API_KEY="your_key_here"
   
   # Run the server
   uv run src/alpha_vantage_mcp/server.py
   
   # Or with inspector for debugging
   npx @modelcontextprotocol/inspector uv run src/alpha_vantage_mcp/server.py
   ```

## Available Tools Overview

### Core Alpha Vantage Tools
- `get-stock-quote` - Real-time stock quotes
- `get-company-info` - Company information and fundamentals
- `get-crypto-exchange-rate` - Cryptocurrency exchange rates
- `get-time-series` - Historical stock price data
- `get-historical-options` - Options chain data
- `get-crypto-daily/weekly/monthly` - Crypto time series

### New Multi-Source Tools
- `get-yahoo-quote` - Yahoo Finance stock data
- `get-eodhd-fundamentals` - Detailed fundamental analysis
- `get-insider-transactions` - Insider trading history
- `get-company-news` - Company-specific news (FinHub)
- `get-market-news` - General market news (FinHub)
- `get-reddit-sentiment` - Reddit community sentiment
- `get-twitter-sentiment` - Twitter social sentiment

## API Requirements

### Required
- **Alpha Vantage API Key**: Core functionality - [Get API Key](https://www.alphavantage.co/support/#api-key)

### Optional (for enhanced features)
- **EODHD API Key**: Fundamentals, insider transactions - [Get API Key](https://eodhistoricaldata.com/r/?ref=DHY3H8NT)
- **FinHub API Key**: Financial news - [Get API Key](https://finnhub.io/register)
- **Twitter Bearer Token**: Social sentiment - [Developer Portal](https://developer.twitter.com/)

### Free (no registration required)
- **Yahoo Finance**: Basic stock data (some endpoints)
- **Reddit**: Community sentiment via public API

## Sample Claude Conversations

Once configured, you can ask Claude questions like:

> "Get me the current stock quote for Apple from both Alpha Vantage and Yahoo Finance, and also check what Reddit thinks about the stock"

> "Show me Tesla's fundamental analysis from EODHD and any recent insider transactions"

> "What's the market news today, and what's the sentiment around GameStop on social media?"

The server will automatically use the appropriate APIs to fetch and format the requested data.