from typing import Any, List, Dict, Optional
import asyncio
import httpx
from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
import mcp.server.stdio
import os

# Import functions from tools.py
from .tools import (
    make_alpha_request,
    make_yahoo_request,
    make_eodhd_request,
    make_finhub_request,
    get_reddit_sentiment,
    get_twitter_sentiment,
    format_quote,
    format_company_info,
    format_crypto_rate,
    format_time_series,
    format_historical_options,
    format_crypto_time_series,
    format_yahoo_quote,
    format_eodhd_fundamentals,
    format_insider_transactions,
    format_news_data,
    format_reddit_sentiment,
    format_twitter_sentiment,
    ALPHA_VANTAGE_BASE,
    API_KEY
)

if not API_KEY:
    raise ValueError("Missing ALPHA_VANTAGE_API_KEY environment variable")

server = Server("alpha_vantage_finance")

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """
    List available tools.
    Each tool specifies its arguments using JSON Schema validation.
    """
    return [
        types.Tool(
            name="get-stock-quote",
            description="Get current stock quote information",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Stock symbol (e.g., AAPL, MSFT)",
                    },
                },
                "required": ["symbol"],
            },
        ),
        types.Tool(
            name="get-company-info",
            description="Get detailed company information",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Stock symbol (e.g., AAPL, MSFT)",
                    },
                },
                "required": ["symbol"],
            },
        ),
        types.Tool(
            name="get-crypto-exchange-rate",
            description="Get current cryptocurrency exchange rate",
            inputSchema={
                "type": "object",
                "properties": {
                    "crypto_symbol": {
                        "type": "string",
                        "description": "Cryptocurrency symbol (e.g., BTC, ETH)",
                    },
                    "market": {
                        "type": "string",
                        "description": "Market currency (e.g., USD, EUR)",
                        "default": "USD"
                    }
                },
                "required": ["crypto_symbol"],
            },
        ),
        types.Tool(
            name="get-time-series",
            description="Get daily time series data for a stock",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Stock symbol (e.g., AAPL, MSFT)",
                    },
                    "outputsize": {
                        "type": "string",
                        "description": "compact (latest 100 data points) or full (up to 20 years of data)",
                        "enum": ["compact", "full"],
                        "default": "compact"
                    }
                },
                "required": ["symbol"],
            },
        ),
        types.Tool(
            name="get-historical-options",
            description="Get historical options chain data for a stock with sorting capabilities",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Stock symbol (e.g., AAPL, MSFT)",
                    },
                    "date": {
                        "type": "string",
                        "description": "Optional: Trading date in YYYY-MM-DD format (defaults to previous trading day, must be after 2008-01-01)",
                        "pattern": "^20[0-9]{2}-(?:0[1-9]|1[0-2])-(?:0[1-9]|[12][0-9]|3[01])$"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Optional: Number of contracts to return (default: 10, use -1 for all contracts)",
                        "default": 10,
                        "minimum": -1
                    },
                    "sort_by": {
                        "type": "string",
                        "description": "Optional: Field to sort by",
                        "enum": [
                            "strike",
                            "expiration",
                            "volume",
                            "open_interest",
                            "implied_volatility",
                            "delta",
                            "gamma",
                            "theta",
                            "vega",
                            "rho",
                            "last",
                            "bid",
                            "ask"
                        ],
                        "default": "strike"
                    },
                    "sort_order": {
                        "type": "string",
                        "description": "Optional: Sort order",
                        "enum": ["asc", "desc"],
                        "default": "asc"
                    }
                },
                "required": ["symbol"],
            },
        ),
        types.Tool(
            name="get-crypto-daily",
            description="Get daily time series data for a cryptocurrency",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Cryptocurrency symbol (e.g., BTC, ETH)",
                    },
                    "market": {
                        "type": "string",
                        "description": "Market currency (e.g., USD, EUR)",
                        "default": "USD"
                    }
                },
                "required": ["symbol"],
            },
        ),
        types.Tool(
            name="get-crypto-weekly",
            description="Get weekly time series data for a cryptocurrency",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Cryptocurrency symbol (e.g., BTC, ETH)",
                    },
                    "market": {
                        "type": "string",
                        "description": "Market currency (e.g., USD, EUR)",
                        "default": "USD"
                    }
                },
                "required": ["symbol"],
            },
        ),
        types.Tool(
            name="get-crypto-monthly",
            description="Get monthly time series data for a cryptocurrency",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Cryptocurrency symbol (e.g., BTC, ETH)",
                    },
                    "market": {
                        "type": "string",
                        "description": "Market currency (e.g., USD, EUR)",
                        "default": "USD"
                    }
                },
                "required": ["symbol"],
            },
        ),
        types.Tool(
            name="get-yahoo-quote",
            description="Get stock quote from Yahoo Finance",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Stock symbol (e.g., AAPL, MSFT)",
                    },
                },
                "required": ["symbol"],
            },
        ),
        types.Tool(
            name="get-eodhd-fundamentals",
            description="Get fundamental company data from EODHD",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Stock symbol (e.g., AAPL.US, MSFT.US)",
                    },
                },
                "required": ["symbol"],
            },
        ),
        types.Tool(
            name="get-insider-transactions",
            description="Get insider trading transactions from EODHD",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Stock symbol (e.g., AAPL.US, MSFT.US)",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Number of transactions to return (default: 50)",
                        "default": 50,
                        "minimum": 1,
                        "maximum": 1000
                    }
                },
                "required": ["symbol"],
            },
        ),
        types.Tool(
            name="get-company-news",
            description="Get company-specific news from FinHub",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Stock symbol (e.g., AAPL, MSFT)",
                    },
                },
                "required": ["symbol"],
            },
        ),
        types.Tool(
            name="get-market-news",
            description="Get general market news from FinHub",
            inputSchema={
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": "News category",
                        "enum": ["general", "forex", "crypto", "merger"],
                        "default": "general"
                    }
                },
            },
        ),
        types.Tool(
            name="get-reddit-sentiment",
            description="Get Reddit sentiment analysis for a stock symbol",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Stock symbol (e.g., AAPL, MSFT)",
                    },
                },
                "required": ["symbol"],
            },
        ),
        types.Tool(
            name="get-twitter-sentiment",
            description="Get Twitter sentiment analysis for a stock symbol",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Stock symbol (e.g., AAPL, MSFT)",
                    },
                },
                "required": ["symbol"],
            },
        )
    ]

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """
    Handle tool execution requests.
    Tools can fetch financial data and notify clients of changes.
    """
    if not arguments:
        return [types.TextContent(type="text", text="Missing arguments for the request")]

    if name == "get-stock-quote":
        symbol = arguments.get("symbol")
        if not symbol:
            return [types.TextContent(type="text", text="Missing symbol parameter")]

        symbol = symbol.upper()

        async with httpx.AsyncClient() as client:
            quote_data = await make_alpha_request(
                client,
                "GLOBAL_QUOTE",
                symbol
            )

            if isinstance(quote_data, str):
                return [types.TextContent(type="text", text=f"Error: {quote_data}")]

            formatted_quote = format_quote(quote_data)
            quote_text = f"Stock quote for {symbol}:\n\n{formatted_quote}"

            return [types.TextContent(type="text", text=quote_text)]

    elif name == "get-company-info":
        symbol = arguments.get("symbol")
        if not symbol:
            return [types.TextContent(type="text", text="Missing symbol parameter")]

        symbol = symbol.upper()

        async with httpx.AsyncClient() as client:
            company_data = await make_alpha_request(
                client,
                "OVERVIEW",
                symbol
            )

            if isinstance(company_data, str):
                return [types.TextContent(type="text", text=f"Error: {company_data}")]

            formatted_info = format_company_info(company_data)
            info_text = f"Company information for {symbol}:\n\n{formatted_info}"

            return [types.TextContent(type="text", text=info_text)]

    elif name == "get-crypto-exchange-rate":
        crypto_symbol = arguments.get("crypto_symbol")
        if not crypto_symbol:
            return [types.TextContent(type="text", text="Missing crypto_symbol parameter")]

        market = arguments.get("market", "USD")
        crypto_symbol = crypto_symbol.upper()
        market = market.upper()

        async with httpx.AsyncClient() as client:
            crypto_data = await make_alpha_request(
                client,
                "CURRENCY_EXCHANGE_RATE",
                None,
                {
                    "from_currency": crypto_symbol,
                    "to_currency": market
                }
            )

            if isinstance(crypto_data, str):
                return [types.TextContent(type="text", text=f"Error: {crypto_data}")]

            formatted_rate = format_crypto_rate(crypto_data)
            rate_text = f"Cryptocurrency exchange rate for {crypto_symbol}/{market}:\n\n{formatted_rate}"

            return [types.TextContent(type="text", text=rate_text)]

    elif name == "get-time-series":
        symbol = arguments.get("symbol")
        if not symbol:
            return [types.TextContent(type="text", text="Missing symbol parameter")]

        symbol = symbol.upper()
        outputsize = arguments.get("outputsize", "compact")

        async with httpx.AsyncClient() as client:
            time_series_data = await make_alpha_request(
                client,
                "TIME_SERIES_DAILY",
                symbol,
                {"outputsize": outputsize}
            )

            if isinstance(time_series_data, str):
                return [types.TextContent(type="text", text=f"Error: {time_series_data}")]

            formatted_series = format_time_series(time_series_data)
            series_text = f"Time series data for {symbol}:\n\n{formatted_series}"

            return [types.TextContent(type="text", text=series_text)]

    elif name == "get-historical-options":
        symbol = arguments.get("symbol")
        date = arguments.get("date")
        limit = arguments.get("limit", 10)
        sort_by = arguments.get("sort_by", "strike")
        sort_order = arguments.get("sort_order", "asc")

        if not symbol:
            return [types.TextContent(type="text", text="Missing symbol parameter")]

        symbol = symbol.upper()

        async with httpx.AsyncClient() as client:
            params = {}
            if date:
                params["date"] = date

            options_data = await make_alpha_request(
                client,
                "HISTORICAL_OPTIONS",
                symbol,
                params
            )

            if isinstance(options_data, str):
                return [types.TextContent(type="text", text=f"Error: {options_data}")]

            formatted_options = format_historical_options(options_data, limit, sort_by, sort_order)
            options_text = f"Historical options data for {symbol}"
            if date:
                options_text += f" on {date}"
            options_text += f":\n\n{formatted_options}"

            return [types.TextContent(type="text", text=options_text)]
            
    elif name == "get-crypto-daily":
        symbol = arguments.get("symbol")
        market = arguments.get("market", "USD")
        
        if not symbol:
            return [types.TextContent(type="text", text="Missing symbol parameter")]

        symbol = symbol.upper()
        market = market.upper()

        async with httpx.AsyncClient() as client:
            crypto_data = await make_alpha_request(
                client,
                "DIGITAL_CURRENCY_DAILY",
                symbol,
                {"market": market}
            )

            if isinstance(crypto_data, str):
                return [types.TextContent(type="text", text=f"Error: {crypto_data}")]

            formatted_data = format_crypto_time_series(crypto_data, "daily")
            data_text = f"Daily cryptocurrency time series for {symbol} in {market}:\n\n{formatted_data}"

            return [types.TextContent(type="text", text=data_text)]
            
    elif name == "get-crypto-weekly":
        symbol = arguments.get("symbol")
        market = arguments.get("market", "USD")
        
        if not symbol:
            return [types.TextContent(type="text", text="Missing symbol parameter")]

        symbol = symbol.upper()
        market = market.upper()

        async with httpx.AsyncClient() as client:
            crypto_data = await make_alpha_request(
                client,
                "DIGITAL_CURRENCY_WEEKLY",
                symbol,
                {"market": market}
            )

            if isinstance(crypto_data, str):
                return [types.TextContent(type="text", text=f"Error: {crypto_data}")]

            formatted_data = format_crypto_time_series(crypto_data, "weekly")
            data_text = f"Weekly cryptocurrency time series for {symbol} in {market}:\n\n{formatted_data}"

            return [types.TextContent(type="text", text=data_text)]
            
    elif name == "get-crypto-monthly":
        symbol = arguments.get("symbol")
        market = arguments.get("market", "USD")
        
        if not symbol:
            return [types.TextContent(type="text", text="Missing symbol parameter")]

        symbol = symbol.upper()
        market = market.upper()

        async with httpx.AsyncClient() as client:
            crypto_data = await make_alpha_request(
                client,
                "DIGITAL_CURRENCY_MONTHLY",
                symbol,
                {"market": market}
            )

            if isinstance(crypto_data, str):
                return [types.TextContent(type="text", text=f"Error: {crypto_data}")]

            formatted_data = format_crypto_time_series(crypto_data, "monthly")
            data_text = f"Monthly cryptocurrency time series for {symbol} in {market}:\n\n{formatted_data}"

            return [types.TextContent(type="text", text=data_text)]
            
    elif name == "get-yahoo-quote":
        symbol = arguments.get("symbol")
        if not symbol:
            return [types.TextContent(type="text", text="Missing symbol parameter")]

        symbol = symbol.upper()

        async with httpx.AsyncClient() as client:
            yahoo_data = await make_yahoo_request(client, "quote", symbol)

            if isinstance(yahoo_data, str):
                return [types.TextContent(type="text", text=f"Error: {yahoo_data}")]

            formatted_data = format_yahoo_quote(yahoo_data)
            data_text = f"Yahoo Finance quote for {symbol}:\n\n{formatted_data}"

            return [types.TextContent(type="text", text=data_text)]
            
    elif name == "get-eodhd-fundamentals":
        symbol = arguments.get("symbol")
        if not symbol:
            return [types.TextContent(type="text", text="Missing symbol parameter")]

        # Ensure proper format for EODHD (e.g., AAPL.US)
        if '.' not in symbol:
            symbol = f"{symbol.upper()}.US"
        else:
            symbol = symbol.upper()

        async with httpx.AsyncClient() as client:
            fundamentals_data = await make_eodhd_request(client, "fundamentals", symbol)

            if isinstance(fundamentals_data, str):
                return [types.TextContent(type="text", text=f"Error: {fundamentals_data}")]

            formatted_data = format_eodhd_fundamentals(fundamentals_data)
            data_text = f"EODHD fundamentals for {symbol}:\n\n{formatted_data}"

            return [types.TextContent(type="text", text=data_text)]
            
    elif name == "get-insider-transactions":
        symbol = arguments.get("symbol")
        limit = arguments.get("limit", 50)
        if not symbol:
            return [types.TextContent(type="text", text="Missing symbol parameter")]

        # Ensure proper format for EODHD
        if '.' not in symbol:
            symbol = f"{symbol.upper()}.US"
        else:
            symbol = symbol.upper()

        async with httpx.AsyncClient() as client:
            insider_data = await make_eodhd_request(
                client, 
                "insider-transactions", 
                additional_params={"code": symbol, "limit": limit}
            )

            if isinstance(insider_data, str):
                return [types.TextContent(type="text", text=f"Error: {insider_data}")]

            formatted_data = format_insider_transactions(insider_data)
            data_text = f"Insider transactions for {symbol}:\n\n{formatted_data}"

            return [types.TextContent(type="text", text=data_text)]
            
    elif name == "get-company-news":
        symbol = arguments.get("symbol")
        if not symbol:
            return [types.TextContent(type="text", text="Missing symbol parameter")]

        symbol = symbol.upper()

        async with httpx.AsyncClient() as client:
            news_data = await make_finhub_request(client, "company-news", symbol)

            if isinstance(news_data, str):
                return [types.TextContent(type="text", text=f"Error: {news_data}")]

            formatted_data = format_news_data(news_data, "FinHub Company")
            data_text = f"Company news for {symbol}:\n\n{formatted_data}"

            return [types.TextContent(type="text", text=data_text)]
            
    elif name == "get-market-news":
        category = arguments.get("category", "general")

        async with httpx.AsyncClient() as client:
            news_data = await make_finhub_request(
                client, 
                "market-news", 
                additional_params={"category": category}
            )

            if isinstance(news_data, str):
                return [types.TextContent(type="text", text=f"Error: {news_data}")]

            formatted_data = format_news_data(news_data, "FinHub Market")
            data_text = f"Market news ({category}):\n\n{formatted_data}"

            return [types.TextContent(type="text", text=data_text)]
            
    elif name == "get-reddit-sentiment":
        symbol = arguments.get("symbol")
        if not symbol:
            return [types.TextContent(type="text", text="Missing symbol parameter")]

        symbol = symbol.upper()

        async with httpx.AsyncClient() as client:
            reddit_data = await get_reddit_sentiment(client, symbol)

            if isinstance(reddit_data, str):
                return [types.TextContent(type="text", text=f"Error: {reddit_data}")]

            formatted_data = format_reddit_sentiment(reddit_data)
            data_text = f"Reddit sentiment for {symbol}:\n\n{formatted_data}"

            return [types.TextContent(type="text", text=data_text)]
            
    elif name == "get-twitter-sentiment":
        symbol = arguments.get("symbol")
        if not symbol:
            return [types.TextContent(type="text", text="Missing symbol parameter")]

        symbol = symbol.upper()

        async with httpx.AsyncClient() as client:
            twitter_data = await get_twitter_sentiment(client, symbol)

            if isinstance(twitter_data, str):
                return [types.TextContent(type="text", text=f"Error: {twitter_data}")]

            formatted_data = format_twitter_sentiment(twitter_data)
            data_text = f"Twitter sentiment for {symbol}:\n\n{formatted_data}"

            return [types.TextContent(type="text", text=data_text)]
    else:
        return [types.TextContent(type="text", text=f"Unknown tool: {name}")]

async def main():
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="alpha_vantage_finance",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

# This is needed if you'd like to connect to a custom client
if __name__ == "__main__":
    asyncio.run(main())
