"""
Multi-Source Financial Data MCP Tools Module

This module contains utility functions for making requests to various financial APIs
and formatting the responses.
"""

from typing import Any, Dict, Optional, List
import httpx
import os
import json
import re
from datetime import datetime, timedelta

# API Base URLs
ALPHA_VANTAGE_BASE = "https://www.alphavantage.co/query"
YAHOO_FINANCE_BASE = "https://query1.finance.yahoo.com"
EODHD_BASE = "https://eodhd.com/api"
FINHUB_BASE = "https://finnhub.io/api/v1"
REUTERS_BASE = "https://api.reuters.com/v1"

# API Keys from environment variables
API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY')
YAHOO_FINANCE_API_KEY = os.getenv('YAHOO_FINANCE_API_KEY')  # Optional for some endpoints
EODHD_API_KEY = os.getenv('EODHD_API_KEY')
FINHUB_API_KEY = os.getenv('FINHUB_API_KEY')
TWITTER_BEARER_TOKEN = os.getenv('TWITTER_BEARER_TOKEN')
REDDIT_CLIENT_ID = os.getenv('REDDIT_CLIENT_ID')
REDDIT_CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET')
BLOOMBERG_API_KEY = os.getenv('BLOOMBERG_API_KEY')
REUTERS_API_KEY = os.getenv('REUTERS_API_KEY')

async def make_alpha_request(client: httpx.AsyncClient, function: str, symbol: Optional[str], additional_params: Optional[Dict[str, Any]] = None) -> Dict[str, Any] | str:
    """Make a request to the Alpha Vantage API with proper error handling.
    
    Args:
        client: An httpx AsyncClient instance
        function: The Alpha Vantage API function to call
        symbol: The stock/crypto symbol (can be None for some endpoints)
        additional_params: Additional parameters to include in the request
        
    Returns:
        Either a dictionary containing the API response, or a string with an error message
    """
    params = {
        "function": function,
        "apikey": API_KEY
    }
    
    if symbol:
        params["symbol"] = symbol
        
    if additional_params:
        params.update(additional_params)

    try:
        response = await client.get(
            ALPHA_VANTAGE_BASE,
            params=params,
            timeout=30.0
        )

        # Check for specific error responses
        if response.status_code == 429:
            return f"Rate limit exceeded. Error details: {response.text}"
        elif response.status_code == 403:
            return f"API key invalid or expired. Error details: {response.text}"

        response.raise_for_status()

        data = response.json()

        # Check for Alpha Vantage specific error messages
        if "Error Message" in data:
            return f"Alpha Vantage API error: {data['Error Message']}"
        if "Note" in data and "API call frequency" in data["Note"]:
            return f"Rate limit warning: {data['Note']}"

        return data
    except httpx.TimeoutException:
        return "Request timed out after 30 seconds. The Alpha Vantage API may be experiencing delays."
    except httpx.ConnectError:
        return "Failed to connect to Alpha Vantage API. Please check your internet connection."
    except httpx.HTTPStatusError as e:
        return f"HTTP error occurred: {str(e)} - Response: {e.response.text}"
    except Exception as e:
        return f"Unexpected error occurred: {str(e)}"


# Yahoo Finance API Functions
async def make_yahoo_request(client: httpx.AsyncClient, endpoint: str, symbol: str, additional_params: Optional[Dict[str, Any]] = None) -> Dict[str, Any] | str:
    """Make a request to the Yahoo Finance API.
    
    Args:
        client: An httpx AsyncClient instance
        endpoint: The Yahoo Finance API endpoint
        symbol: The stock symbol
        additional_params: Additional parameters
        
    Returns:
        Either a dictionary containing the API response, or a string with an error message
    """
    if endpoint == "quote":
        url = f"{YAHOO_FINANCE_BASE}/v8/finance/chart/{symbol}"
        params = {"interval": "1d", "range": "1d"}
    elif endpoint == "news":
        url = f"{YAHOO_FINANCE_BASE}/v1/finance/search"
        params = {"q": symbol, "newsCount": 10}
    else:
        return f"Unknown Yahoo Finance endpoint: {endpoint}"
    
    if additional_params:
        params.update(additional_params)

    try:
        response = await client.get(url, params=params, timeout=30.0)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return f"Yahoo Finance API error: {str(e)}"


# EODHD API Functions
async def make_eodhd_request(client: httpx.AsyncClient, endpoint: str, symbol: Optional[str] = None, additional_params: Optional[Dict[str, Any]] = None) -> Dict[str, Any] | str:
    """Make a request to the EODHD API.
    
    Args:
        client: An httpx AsyncClient instance
        endpoint: The EODHD API endpoint
        symbol: The stock symbol (optional for some endpoints)
        additional_params: Additional parameters
        
    Returns:
        Either a dictionary containing the API response, or a string with an error message
    """
    if not EODHD_API_KEY:
        return "EODHD API key not found. Please set EODHD_API_KEY environment variable."
    
    if endpoint == "eod":
        url = f"{EODHD_BASE}/eod/{symbol}"
    elif endpoint == "fundamentals":
        url = f"{EODHD_BASE}/fundamentals/{symbol}"
    elif endpoint == "insider-transactions":
        url = f"{EODHD_BASE}/insider-transactions"
    elif endpoint == "sentiment":
        url = f"{EODHD_BASE}/sentiments"
    else:
        return f"Unknown EODHD endpoint: {endpoint}"
    
    params = {"api_token": EODHD_API_KEY, "fmt": "json"}
    if additional_params:
        params.update(additional_params)

    try:
        response = await client.get(url, params=params, timeout=30.0)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return f"EODHD API error: {str(e)}"


# FinHub API Functions
async def make_finhub_request(client: httpx.AsyncClient, endpoint: str, symbol: Optional[str] = None, additional_params: Optional[Dict[str, Any]] = None) -> Dict[str, Any] | str:
    """Make a request to the FinHub API.
    
    Args:
        client: An httpx AsyncClient instance
        endpoint: The FinHub API endpoint
        symbol: The stock symbol (optional for some endpoints)
        additional_params: Additional parameters
        
    Returns:
        Either a dictionary containing the API response, or a string with an error message
    """
    if not FINHUB_API_KEY:
        return "FinHub API key not found. Please set FINHUB_API_KEY environment variable."
    
    if endpoint == "company-news":
        url = f"{FINHUB_BASE}/company-news"
        params = {"symbol": symbol, "token": FINHUB_API_KEY}
        # Add date range for recent news
        to_date = datetime.now().strftime("%Y-%m-%d")
        from_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        params.update({"from": from_date, "to": to_date})
    elif endpoint == "market-news":
        url = f"{FINHUB_BASE}/news"
        params = {"category": "general", "token": FINHUB_API_KEY}
    elif endpoint == "sentiment":
        url = f"{FINHUB_BASE}/news-sentiment"
        params = {"symbol": symbol, "token": FINHUB_API_KEY}
    else:
        return f"Unknown FinHub endpoint: {endpoint}"
    
    if additional_params:
        params.update(additional_params)

    try:
        response = await client.get(url, params=params, timeout=30.0)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return f"FinHub API error: {str(e)}"


# Social Media API Functions
async def get_reddit_sentiment(client: httpx.AsyncClient, symbol: str) -> Dict[str, Any] | str:
    """Get Reddit sentiment for a stock symbol.
    
    Args:
        client: An httpx AsyncClient instance
        symbol: The stock symbol
        
    Returns:
        Either a dictionary containing Reddit data, or a string with an error message
    """
    try:
        # Search for stock mentions in popular finance subreddits
        subreddits = ["stocks", "investing", "wallstreetbets", "SecurityAnalysis", "ValueInvesting"]
        url = f"https://www.reddit.com/r/{'+'.join(subreddits)}/search.json"
        params = {
            "q": f"${symbol}",
            "limit": 25,
            "sort": "hot",
            "t": "week"
        }
        
        headers = {"User-Agent": "AlphaVantage-MCP/1.0"}
        response = await client.get(url, params=params, headers=headers, timeout=30.0)
        response.raise_for_status()
        
        data = response.json()
        posts = []
        
        for post in data.get("data", {}).get("children", []):
            post_data = post.get("data", {})
            posts.append({
                "title": post_data.get("title", ""),
                "score": post_data.get("score", 0),
                "num_comments": post_data.get("num_comments", 0),
                "subreddit": post_data.get("subreddit", ""),
                "created": post_data.get("created_utc", 0),
                "url": post_data.get("url", "")
            })
        
        return {"posts": posts, "total_posts": len(posts)}
        
    except Exception as e:
        return f"Reddit API error: {str(e)}"


async def get_twitter_sentiment(client: httpx.AsyncClient, symbol: str) -> Dict[str, Any] | str:
    """Get Twitter sentiment for a stock symbol.
    
    Args:
        client: An httpx AsyncClient instance
        symbol: The stock symbol
        
    Returns:
        Either a dictionary containing Twitter data, or a string with an error message
    """
    if not TWITTER_BEARER_TOKEN:
        return "Twitter Bearer Token not found. Please set TWITTER_BEARER_TOKEN environment variable."
    
    try:
        url = "https://api.twitter.com/2/tweets/search/recent"
        params = {
            "query": f"${symbol} OR #{symbol}",
            "max_results": 100,
            "tweet.fields": "created_at,public_metrics,context_annotations"
        }
        
        headers = {"Authorization": f"Bearer {TWITTER_BEARER_TOKEN}"}
        response = await client.get(url, params=params, headers=headers, timeout=30.0)
        response.raise_for_status()
        
        return response.json()
        
    except Exception as e:
        return f"Twitter API error: {str(e)}"


def format_quote(quote_data: Dict[str, Any]) -> str:
    """Format quote data into a concise string.
    
    Args:
        quote_data: The response data from the Alpha Vantage Global Quote endpoint
        
    Returns:
        A formatted string containing the quote information
    """
    try:
        global_quote = quote_data.get("Global Quote", {})
        if not global_quote:
            return "No quote data available in the response"

        return (
            f"Price: ${global_quote.get('05. price', 'N/A')}\n"
            f"Change: ${global_quote.get('09. change', 'N/A')} "
            f"({global_quote.get('10. change percent', 'N/A')})\n"
            f"Volume: {global_quote.get('06. volume', 'N/A')}\n"
            f"High: ${global_quote.get('03. high', 'N/A')}\n"
            f"Low: ${global_quote.get('04. low', 'N/A')}\n"
            "---"
        )
    except Exception as e:
        return f"Error formatting quote data: {str(e)}"


def format_company_info(overview_data: Dict[str, Any]) -> str:
    """Format company information into a concise string.
    
    Args:
        overview_data: The response data from the Alpha Vantage OVERVIEW endpoint
        
    Returns:
        A formatted string containing the company information
    """
    try:
        if not overview_data:
            return "No company information available in the response"

        return (
            f"Name: {overview_data.get('Name', 'N/A')}\n"
            f"Sector: {overview_data.get('Sector', 'N/A')}\n"
            f"Industry: {overview_data.get('Industry', 'N/A')}\n"
            f"Market Cap: ${overview_data.get('MarketCapitalization', 'N/A')}\n"
            f"Description: {overview_data.get('Description', 'N/A')}\n"
            f"Exchange: {overview_data.get('Exchange', 'N/A')}\n"
            f"Currency: {overview_data.get('Currency', 'N/A')}\n"
            "---"
        )
    except Exception as e:
        return f"Error formatting company data: {str(e)}"


def format_crypto_rate(crypto_data: Dict[str, Any]) -> str:
    """Format cryptocurrency exchange rate data into a concise string.
    
    Args:
        crypto_data: The response data from the Alpha Vantage CURRENCY_EXCHANGE_RATE endpoint
        
    Returns:
        A formatted string containing the cryptocurrency exchange rate information
    """
    try:
        realtime_data = crypto_data.get("Realtime Currency Exchange Rate", {})
        if not realtime_data:
            return "No exchange rate data available in the response"

        return (
            f"From: {realtime_data.get('2. From_Currency Name', 'N/A')} ({realtime_data.get('1. From_Currency Code', 'N/A')})\n"
            f"To: {realtime_data.get('4. To_Currency Name', 'N/A')} ({realtime_data.get('3. To_Currency Code', 'N/A')})\n"
            f"Exchange Rate: {realtime_data.get('5. Exchange Rate', 'N/A')}\n"
            f"Last Updated: {realtime_data.get('6. Last Refreshed', 'N/A')} {realtime_data.get('7. Time Zone', 'N/A')}\n"
            f"Bid Price: {realtime_data.get('8. Bid Price', 'N/A')}\n"
            f"Ask Price: {realtime_data.get('9. Ask Price', 'N/A')}\n"
            "---"
        )
    except Exception as e:
        return f"Error formatting cryptocurrency data: {str(e)}"


def format_time_series(time_series_data: Dict[str, Any]) -> str:
    """Format time series data into a concise string.
    
    Args:
        time_series_data: The response data from the Alpha Vantage TIME_SERIES_DAILY endpoint
        
    Returns:
        A formatted string containing the time series information
    """
    try:
        # Get the daily time series data
        time_series = time_series_data.get("Time Series (Daily)", {})
        if not time_series:
            return "No time series data available in the response"

        # Get metadata
        metadata = time_series_data.get("Meta Data", {})
        symbol = metadata.get("2. Symbol", "Unknown")
        last_refreshed = metadata.get("3. Last Refreshed", "Unknown")

        # Format the most recent 5 days of data
        formatted_data = [
            f"Time Series Data for {symbol} (Last Refreshed: {last_refreshed})\n\n"
        ]

        for date, values in list(time_series.items())[:5]:
            formatted_data.append(
                f"Date: {date}\n"
                f"Open: ${values.get('1. open', 'N/A')}\n"
                f"High: ${values.get('2. high', 'N/A')}\n"
                f"Low: ${values.get('3. low', 'N/A')}\n"
                f"Close: ${values.get('4. close', 'N/A')}\n"
                f"Volume: {values.get('5. volume', 'N/A')}\n"
                "---\n"
            )

        return "\n".join(formatted_data)
    except Exception as e:
        return f"Error formatting time series data: {str(e)}"


def format_crypto_time_series(time_series_data: Dict[str, Any], series_type: str) -> str:
    """Format cryptocurrency time series data into a concise string.
    
    Args:
        time_series_data: The response data from Alpha Vantage Digital Currency endpoints
        series_type: Type of time series (daily, weekly, monthly)
        
    Returns:
        A formatted string containing the cryptocurrency time series information
    """
    try:
        # Determine the time series key based on series_type
        time_series_key = ""
        if series_type == "daily":
            time_series_key = "Time Series (Digital Currency Daily)"
        elif series_type == "weekly":
            time_series_key = "Time Series (Digital Currency Weekly)"
        elif series_type == "monthly":
            time_series_key = "Time Series (Digital Currency Monthly)"
        else:
            return f"Unknown series type: {series_type}"
            
        # Get the time series data
        time_series = time_series_data.get(time_series_key, {})
        if not time_series:
            all_keys = ", ".join(time_series_data.keys())
            return f"No cryptocurrency time series data found with key: '{time_series_key}'.\nAvailable keys: {all_keys}"

        # Get metadata
        metadata = time_series_data.get("Meta Data", {})
        crypto_symbol = metadata.get("2. Digital Currency Code", "Unknown")
        crypto_name = metadata.get("3. Digital Currency Name", "Unknown")
        market = metadata.get("4. Market Code", "Unknown")
        market_name = metadata.get("5. Market Name", "Unknown")
        last_refreshed = metadata.get("6. Last Refreshed", "Unknown")
        time_zone = metadata.get("7. Time Zone", "Unknown")

        # Format the header
        formatted_data = [
            f"{series_type.capitalize()} Time Series for {crypto_name} ({crypto_symbol})",
            f"Market: {market_name} ({market})",
            f"Last Refreshed: {last_refreshed} {time_zone}",
            ""
        ]

        # Format the most recent 5 data points
        for date, values in list(time_series.items())[:5]:
            # Get price information - based on the API response, we now know the correct field names
            open_price = values.get("1. open", "N/A")
            high_price = values.get("2. high", "N/A")
            low_price = values.get("3. low", "N/A")
            close_price = values.get("4. close", "N/A")
            volume = values.get("5. volume", "N/A")
            
            formatted_data.append(f"Date: {date}")
            formatted_data.append(f"Open: {open_price} {market}")
            formatted_data.append(f"High: {high_price} {market}")
            formatted_data.append(f"Low: {low_price} {market}")
            formatted_data.append(f"Close: {close_price} {market}")
            formatted_data.append(f"Volume: {volume}")
            formatted_data.append("---")
        
        return "\n".join(formatted_data)
    except Exception as e:
        return f"Error formatting cryptocurrency time series data: {str(e)}"


def format_historical_options(options_data: Dict[str, Any], limit: int = 10, sort_by: str = "strike", sort_order: str = "asc") -> str:
    """Format historical options chain data into a concise string with sorting.
    
    Args:
        options_data: The response data from the Alpha Vantage HISTORICAL_OPTIONS endpoint
        limit: Number of contracts to return (-1 for all)
        sort_by: Field to sort by
        sort_order: Sort order (asc or desc)
        
    Returns:
        A formatted string containing the historical options information
    """
    try:
        if "Error Message" in options_data:
            return f"Error: {options_data['Error Message']}"

        options_chain = options_data.get("data", [])

        if not options_chain:
            return "No options data available in the response"

        formatted = [
            f"Historical Options Data:\n",
            f"Status: {options_data.get('message', 'N/A')}\n",
            f"Sorted by: {sort_by} ({sort_order})\n\n"
        ]

        # Convert string values to float for numeric sorting
        def get_sort_key(contract):
            value = contract.get(sort_by, 0)
            try:
                # Remove $ and % signs if present
                if isinstance(value, str):
                    value = value.replace('$', '').replace('%', '')
                return float(value)
            except (ValueError, TypeError):
                return value

        # Sort the options chain
        sorted_chain = sorted(
            options_chain,
            key=get_sort_key,
            reverse=(sort_order == "desc")
        )

        # If limit is -1, show all contracts
        display_contracts = sorted_chain if limit == -1 else sorted_chain[:limit]

        for contract in display_contracts:
            formatted.append(f"Contract Details:\n")
            formatted.append(f"Contract ID: {contract.get('contractID', 'N/A')}\n")
            formatted.append(f"Expiration: {contract.get('expiration', 'N/A')}\n")
            formatted.append(f"Strike: ${contract.get('strike', 'N/A')}\n")
            formatted.append(f"Type: {contract.get('type', 'N/A')}\n")
            formatted.append(f"Last: ${contract.get('last', 'N/A')}\n")
            formatted.append(f"Mark: ${contract.get('mark', 'N/A')}\n")
            formatted.append(f"Bid: ${contract.get('bid', 'N/A')} (Size: {contract.get('bid_size', 'N/A')})\n")
            formatted.append(f"Ask: ${contract.get('ask', 'N/A')} (Size: {contract.get('ask_size', 'N/A')})\n")
            formatted.append(f"Volume: {contract.get('volume', 'N/A')}\n")
            formatted.append(f"Open Interest: {contract.get('open_interest', 'N/A')}\n")
            formatted.append(f"IV: {contract.get('implied_volatility', 'N/A')}\n")
            formatted.append(f"Delta: {contract.get('delta', 'N/A')}\n")
            formatted.append(f"Gamma: {contract.get('gamma', 'N/A')}\n")
            formatted.append(f"Theta: {contract.get('theta', 'N/A')}\n")
            formatted.append(f"Vega: {contract.get('vega', 'N/A')}\n")
            formatted.append(f"Rho: {contract.get('rho', 'N/A')}\n")
            formatted.append("---\n")

        if limit != -1 and len(sorted_chain) > limit:
            formatted.append(f"\n... and {len(sorted_chain) - limit} more contracts")

        return "".join(formatted)
    except Exception as e:
        return f"Error formatting options data: {str(e)}"


# Formatting functions for new APIs

def format_yahoo_quote(data: Dict[str, Any]) -> str:
    """Format Yahoo Finance quote data."""
    try:
        chart = data.get("chart", {})
        if not chart or "result" not in chart or not chart["result"]:
            return "No Yahoo Finance data available"
        
        result = chart["result"][0]
        meta = result.get("meta", {})
        
        return (
            f"Yahoo Finance Data:\n"
            f"Symbol: {meta.get('symbol', 'N/A')}\n"
            f"Price: ${meta.get('regularMarketPrice', 'N/A')}\n"
            f"Previous Close: ${meta.get('previousClose', 'N/A')}\n"
            f"Volume: {meta.get('regularMarketVolume', 'N/A')}\n"
            f"Market Cap: {meta.get('marketCap', 'N/A')}\n"
            f"Currency: {meta.get('currency', 'N/A')}\n"
            "---"
        )
    except Exception as e:
        return f"Error formatting Yahoo Finance data: {str(e)}"


def format_eodhd_fundamentals(data: Dict[str, Any]) -> str:
    """Format EODHD fundamentals data."""
    try:
        if isinstance(data, str):
            return data
        
        general = data.get("General", {})
        highlights = data.get("Highlights", {})
        valuation = data.get("Valuation", {})
        
        return (
            f"EODHD Fundamentals:\n"
            f"Company: {general.get('Name', 'N/A')}\n"
            f"Sector: {general.get('Sector', 'N/A')}\n"
            f"Industry: {general.get('Industry', 'N/A')}\n"
            f"Market Cap: ${highlights.get('MarketCapitalization', 'N/A')}\n"
            f"P/E Ratio: {valuation.get('TrailingPE', 'N/A')}\n"
            f"EPS: ${highlights.get('EarningsShare', 'N/A')}\n"
            f"Revenue: ${highlights.get('RevenueTTM', 'N/A')}\n"
            "---"
        )
    except Exception as e:
        return f"Error formatting EODHD fundamentals: {str(e)}"


def format_insider_transactions(data: List[Dict[str, Any]] | str) -> str:
    """Format insider transactions data."""
    try:
        if isinstance(data, str):
            return data
        
        if not data or not isinstance(data, list):
            return "No insider transaction data available"
        
        formatted = ["Recent Insider Transactions:\n"]
        
        for transaction in data[:10]:  # Show last 10 transactions
            formatted.append(
                f"Date: {transaction.get('date', 'N/A')}\n"
                f"Name: {transaction.get('fullName', 'N/A')}\n"
                f"Position: {transaction.get('position', 'N/A')}\n"
                f"Transaction: {transaction.get('transactionType', 'N/A')}\n"
                f"Shares: {transaction.get('sharesTransacted', 'N/A')}\n"
                f"Price: ${transaction.get('price', 'N/A')}\n"
                "---\n"
            )
        
        return "".join(formatted)
    except Exception as e:
        return f"Error formatting insider transactions: {str(e)}"


def format_news_data(data: List[Dict[str, Any]] | str, source: str = "FinHub") -> str:
    """Format news data from various sources."""
    try:
        if isinstance(data, str):
            return data
        
        if not data or not isinstance(data, list):
            return f"No {source} news data available"
        
        formatted = [f"{source} Financial News:\n"]
        
        for article in data[:10]:  # Show last 10 articles
            formatted.append(
                f"Headline: {article.get('headline', article.get('title', 'N/A'))}\n"
                f"Summary: {article.get('summary', article.get('description', 'N/A'))[:200]}...\n"
                f"Source: {article.get('source', 'N/A')}\n"
                f"URL: {article.get('url', 'N/A')}\n"
                f"Date: {datetime.fromtimestamp(article.get('datetime', 0)).strftime('%Y-%m-%d %H:%M:%S') if article.get('datetime') else 'N/A'}\n"
                "---\n"
            )
        
        return "".join(formatted)
    except Exception as e:
        return f"Error formatting {source} news data: {str(e)}"


def format_reddit_sentiment(data: Dict[str, Any] | str) -> str:
    """Format Reddit sentiment data."""
    try:
        if isinstance(data, str):
            return data
        
        posts = data.get("posts", [])
        if not posts:
            return "No Reddit discussions found for this symbol"
        
        formatted = [f"Reddit Sentiment Analysis:\n"]
        formatted.append(f"Total Posts Found: {data.get('total_posts', 0)}\n\n")
        
        # Calculate basic sentiment metrics
        total_score = sum(post.get("score", 0) for post in posts)
        avg_score = total_score / len(posts) if posts else 0
        
        formatted.append(f"Average Post Score: {avg_score:.1f}\n")
        formatted.append(f"Total Combined Score: {total_score}\n\n")
        formatted.append("Recent Popular Posts:\n")
        
        # Sort by score and show top posts
        sorted_posts = sorted(posts, key=lambda x: x.get("score", 0), reverse=True)
        
        for post in sorted_posts[:5]:
            formatted.append(
                f"Title: {post.get('title', 'N/A')[:100]}...\n"
                f"Score: {post.get('score', 0)} | Comments: {post.get('num_comments', 0)}\n"
                f"Subreddit: r/{post.get('subreddit', 'N/A')}\n"
                "---\n"
            )
        
        return "".join(formatted)
    except Exception as e:
        return f"Error formatting Reddit sentiment: {str(e)}"


def format_twitter_sentiment(data: Dict[str, Any] | str) -> str:
    """Format Twitter sentiment data."""
    try:
        if isinstance(data, str):
            return data
        
        tweets = data.get("data", [])
        if not tweets:
            return "No Twitter mentions found for this symbol"
        
        formatted = [f"Twitter Sentiment Analysis:\n"]
        formatted.append(f"Total Tweets Found: {len(tweets)}\n\n")
        
        formatted.append("Recent Tweets:\n")
        
        for tweet in tweets[:10]:
            metrics = tweet.get("public_metrics", {})
            formatted.append(
                f"Tweet: {tweet.get('text', 'N/A')[:150]}...\n"
                f"Likes: {metrics.get('like_count', 0)} | Retweets: {metrics.get('retweet_count', 0)}\n"
                f"Date: {tweet.get('created_at', 'N/A')}\n"
                "---\n"
            )
        
        return "".join(formatted)
    except Exception as e:
        return f"Error formatting Twitter sentiment: {str(e)}"
