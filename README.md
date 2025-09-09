# Multi-Source Financial Data MCP Server
[![smithery badge](https://smithery.ai/badge/@berlinbra/alpha-vantage-mcp)](https://smithery.ai/server/@berlinbra/alpha-vantage-mcp)

A comprehensive Model Context Protocol (MCP) server that provides real-time access to financial market data through multiple APIs including [Alpha Vantage](https://www.alphavantage.co/documentation/), Yahoo Finance, EODHD, FinHub, and social media sentiment analysis. This server implements a standardized interface for retrieving stock quotes, company information, news, and market sentiment.

<a href="https://glama.ai/mcp/servers/0wues5td08"><img width="380" height="200" src="https://glama.ai/mcp/servers/0wues5td08/badge" alt="AlphaVantage-MCP MCP server" /></a>

# Features

## Market Data & Trading
- Real-time stock quotes with price, volume, and change data (Alpha Vantage + Yahoo Finance)
- Detailed company information including sector, industry, and market cap
- Real-time cryptocurrency exchange rates with bid/ask prices
- Daily, weekly, and monthly cryptocurrency time series data
- Historical options chain data with advanced filtering and sorting

## Fundamental Analysis
- Company fundamentals from EODHD (P/E ratios, EPS, revenue, etc.)
- Insider trading transactions and analysis
- Financial history and key metrics
- Company profiles and business descriptions

## News & Market Intelligence
- Company-specific news from FinHub
- General market news across multiple categories
- Real-time news sentiment analysis
- Multiple news source integration

## Social Media Sentiment
- Twitter/X sentiment analysis for stock mentions
- Reddit sentiment from popular finance subreddits
- Social media trend analysis and scoring
- Community discussion tracking

## Technical Features
- Built-in error handling and rate limit management
- Multi-API fallback support
- Comprehensive data formatting
- Environment-based configuration

## Installation

### Using Claude Desktop

#### Installing via Docker

- Clone the repository and build a local image to be utilized by your Claude desktop client

```sh
cd alpha-vantage-mcp
docker build -t mcp/alpha-vantage .
```

- Change your `claude_desktop_config.json` to match the following, replacing `REPLACE_API_KEY` with your actual key:

 > `claude_desktop_config.json` path
 >
 > - On MacOS: `~/Library/Application\ Support/Claude/claude_desktop_config.json`
 > - On Windows: `%APPDATA%/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "alphavantage": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "-e",
        "ALPHA_VANTAGE_API_KEY",
        "mcp/alpha-vantage"
      ],
      "env": {
        "ALPHA_VANTAGE_API_KEY": "REPLACE_API_KEY"
      }
    }
  }
}
```

#### Installing via Smithery

To install Alpha Vantage MCP Server for Claude Desktop automatically via [Smithery](https://smithery.ai/server/@berlinbra/alpha-vantage-mcp):

```bash
npx -y @smithery/cli install @berlinbra/alpha-vantage-mcp --client claude
```

<summary> <h3> Development/Unpublished Servers Configuration <h3> </summary>

<details>

```json
{
 "mcpServers": {
  "alpha-vantage-mcp": {
   "args": [
    "--directory",
    "/Users/{INSERT_USER}/YOUR/PATH/TO/alpha-vantage-mcp",
    "run",
    "alpha-vantage-mcp"
   ],
   "command": "uv",
   "env": {
    "ALPHA_VANTAGE_API_KEY": "<insert api key>"
   }
  }
 }
}
```
        
</details>

#### Install packages

```
uv install -e .
```

#### Running

After connecting Claude client with the MCP tool via json file and installing the packages, Claude should see the server's mcp tools:

You can run the sever yourself via:
In alpha-vantage-mcp repo: 
```
uv run src/alpha_vantage_mcp/server.py
```

with inspector
```
* npx @modelcontextprotocol/inspector uv --directory /Users/{INSERT_USER}/YOUR/PATH/TO/alpha-vantage-mcp run src/alpha_vantage_mcp/server.py `
```

## Available Tools

The server implements fifteen tools across multiple financial data providers:

### Alpha Vantage Tools (Core)
- `get-stock-quote`: Get the latest stock quote for a specific company
- `get-company-info`: Get stock-related information for a specific company
- `get-crypto-exchange-rate`: Get current cryptocurrency exchange rates
- `get-time-series`: Get historical daily price data for a stock
- `get-historical-options`: Get historical options chain data with sorting capabilities
- `get-crypto-daily`: Get daily time series data for a cryptocurrency
- `get-crypto-weekly`: Get weekly time series data for a cryptocurrency
- `get-crypto-monthly`: Get monthly time series data for a cryptocurrency

### Yahoo Finance Tools
- `get-yahoo-quote`: Get stock quote from Yahoo Finance with additional metadata

### EODHD Tools
- `get-eodhd-fundamentals`: Get comprehensive fundamental analysis data
- `get-insider-transactions`: Get insider trading transaction history

### FinHub Tools
- `get-company-news`: Get company-specific financial news
- `get-market-news`: Get general market news across categories

### Social Media Tools
- `get-reddit-sentiment`: Get Reddit sentiment analysis from finance subreddits
- `get-twitter-sentiment`: Get Twitter sentiment analysis for stock mentions

### get-stock-quote

**Input Schema:**
```json
{
    "symbol": {
        "type": "string",
        "description": "Stock symbol (e.g., AAPL, MSFT)"
    }
}
```

**Example Response:**
```
Stock quote for AAPL:

Price: $198.50
Change: $2.50 (+1.25%)
Volume: 58942301
High: $199.62
Low: $197.20
```

### get-company-info

Retrieves detailed company information for a given symbol.

**Input Schema:**
```json
{
    "symbol": {
        "type": "string",
        "description": "Stock symbol (e.g., AAPL, MSFT)"
    }
}
```

**Example Response:**
```
Company information for AAPL:

Name: Apple Inc
Sector: Technology
Industry: Consumer Electronics
Market Cap: $3000000000000
Description: Apple Inc. designs, manufactures, and markets smartphones...
Exchange: NASDAQ
Currency: USD
```

### get-crypto-exchange-rate

Retrieves real-time cryptocurrency exchange rates with additional market data.

**Input Schema:**
```json
{
    "crypto_symbol": {
        "type": "string",
        "description": "Cryptocurrency symbol (e.g., BTC, ETH)"
    },
    "market": {
        "type": "string",
        "description": "Market currency (e.g., USD, EUR)",
        "default": "USD"
    }
}
```

**Example Response:**
```
Cryptocurrency exchange rate for BTC/USD:

From: Bitcoin (BTC)
To: United States Dollar (USD)
Exchange Rate: 43521.45000
Last Updated: 2024-12-17 19:45:00 UTC
Bid Price: 43521.00000
Ask Price: 43522.00000
```

### get-time-series

Retrieves daily time series (OHLCV) data.

**Input Schema:**
```json
{
    "symbol": {
        "type": "string",
        "description": "Stock symbol (e.g., AAPL, MSFT)"
    },
    "outputsize": {
        "type": "string",
        "description": "compact (latest 100 data points) or full (up to 20 years of data)",
        "default": "compact"
    }
}
```
**Example Response:**
```
Time Series Data for AAPL (Last Refreshed: 2024-12-17 16:00:00):

Date: 2024-12-16
Open: $195.09
High: $197.68
Low: $194.83
Close: $197.57
Volume: 55,751,011
```

### get-historical-options

Retrieves historical options chain data with advanced sorting and filtering capabilities.

**Input Schema:**
```json
{
    "symbol": {
        "type": "string",
        "description": "Stock symbol (e.g., AAPL, MSFT)"
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
        "enum": ["strike", "expiration", "volume", "open_interest", "implied_volatility", "delta", "gamma", "theta", "vega", "rho", "last", "bid", "ask"],
        "default": "strike"
    },
    "sort_order": {
        "type": "string",
        "description": "Optional: Sort order",
        "enum": ["asc", "desc"],
        "default": "asc"
    }
}
```

**Example Response:**
```
Historical Options Data for AAPL (2024-02-20):

Contract 1:
Strike: $190.00
Expiration: 2024-03-15
Last: $8.45
Bid: $8.40
Ask: $8.50
Volume: 1245
Open Interest: 4567
Implied Volatility: 0.25
Greeks:
  Delta: 0.65
  Gamma: 0.04
  Theta: -0.15
  Vega: 0.30
  Rho: 0.25

Contract 2:
...
```

### get-crypto-daily

Retrieves daily time series data for a cryptocurrency.

**Input Schema:**
```json
{
    "symbol": {
        "type": "string",
        "description": "Cryptocurrency symbol (e.g., BTC, ETH)"
    },
    "market": {
        "type": "string",
        "description": "Market currency (e.g., USD, EUR)",
        "default": "USD"
    }
}
```

**Example Response:**
```
Daily cryptocurrency time series for SOL in USD:

Daily Time Series for Solana (SOL)
Market: United States Dollar (USD)
Last Refreshed: 2025-04-17 00:00:00 UTC

Date: 2025-04-17
Open: 131.31000000 USD
High: 131.67000000 USD
Low: 130.74000000 USD
Close: 131.15000000 USD
Volume: 39652.22195178
---
Date: 2025-04-16
Open: 126.10000000 USD
High: 133.91000000 USD
Low: 123.46000000 USD
Close: 131.32000000 USD
Volume: 1764240.04195810
---
```

### get-crypto-weekly

Retrieves weekly time series data for a cryptocurrency.

**Input Schema:**
```json
{
    "symbol": {
        "type": "string",
        "description": "Cryptocurrency symbol (e.g., BTC, ETH)"
    },
    "market": {
        "type": "string",
        "description": "Market currency (e.g., USD, EUR)",
        "default": "USD"
    }
}
```

**Example Response:**
```
Weekly cryptocurrency time series for SOL in USD:

Weekly Time Series for Solana (SOL)
Market: United States Dollar (USD)
Last Refreshed: 2025-04-17 00:00:00 UTC

Date: 2025-04-17
Open: 128.32000000 USD
High: 136.00000000 USD
Low: 123.46000000 USD
Close: 131.15000000 USD
Volume: 4823091.05667581
---
Date: 2025-04-13
Open: 105.81000000 USD
High: 134.11000000 USD
Low: 95.16000000 USD
Close: 128.32000000 USD
Volume: 18015328.38860037
---
```

### get-crypto-monthly

Retrieves monthly time series data for a cryptocurrency.

**Input Schema:**
```json
{
    "symbol": {
        "type": "string",
        "description": "Cryptocurrency symbol (e.g., BTC, ETH)"
    },
    "market": {
        "type": "string",
        "description": "Market currency (e.g., USD, EUR)",
        "default": "USD"
    }
}
```

**Example Response:**
```
Monthly cryptocurrency time series for SOL in USD:

Monthly Time Series for Solana (SOL)
Market: United States Dollar (USD)
Last Refreshed: 2025-04-17 00:00:00 UTC

Date: 2025-04-17
Open: 124.51000000 USD
High: 136.18000000 USD
Low: 95.16000000 USD
Close: 131.15000000 USD
Volume: 34268628.85976021
---
Date: 2025-03-31
Open: 148.09000000 USD
High: 180.00000000 USD
Low: 112.00000000 USD
Close: 124.54000000 USD
Volume: 42360395.75443056
---
```

### get-yahoo-quote

**Input Schema:**
```json
{
    "symbol": {
        "type": "string",
        "description": "Stock symbol (e.g., AAPL, MSFT)"
    }
}
```

**Example Response:**
```
Yahoo Finance Data:
Symbol: AAPL
Price: $198.50
Previous Close: $196.00
Volume: 58942301
Market Cap: 3000000000000
Currency: USD
---
```

### get-eodhd-fundamentals

**Input Schema:**
```json
{
    "symbol": {
        "type": "string",
        "description": "Stock symbol (e.g., AAPL.US, MSFT.US)"
    }
}
```

**Example Response:**
```
EODHD Fundamentals:
Company: Apple Inc
Sector: Technology
Industry: Consumer Electronics
Market Cap: $3000000000000
P/E Ratio: 28.5
EPS: $6.95
Revenue: $394000000000
---
```

### get-company-news

**Input Schema:**
```json
{
    "symbol": {
        "type": "string",
        "description": "Stock symbol (e.g., AAPL, MSFT)"
    }
}
```

**Example Response:**
```
FinHub Company News:
Headline: Apple Reports Strong Q4 Earnings
Summary: Apple Inc. reported quarterly earnings that beat analyst expectations...
Source: Reuters
URL: https://example.com/news
Date: 2024-12-17 14:30:00
---
```

### get-reddit-sentiment

**Input Schema:**
```json
{
    "symbol": {
        "type": "string",
        "description": "Stock symbol (e.g., AAPL, MSFT)"
    }
}
```

**Example Response:**
```
Reddit Sentiment Analysis:
Total Posts Found: 25
Average Post Score: 15.2
Total Combined Score: 380

Recent Popular Posts:
Title: AAPL earnings discussion - what are your thoughts?
Score: 45 | Comments: 23
Subreddit: r/stocks
---
```

## API Configuration

The server supports multiple API providers. Copy `.env.sample` to `.env` and configure your API keys:

```bash
cp .env.sample .env
# Edit .env with your API keys
```

### Required APIs
- **Alpha Vantage**: Core functionality (REQUIRED)

### Optional APIs
- **EODHD**: Fundamental analysis and insider transactions
- **FinHub**: Financial news and market data
- **Twitter**: Social media sentiment analysis  
- **Reddit**: Community sentiment (uses public API, no key required)
- **Yahoo Finance**: Additional market data (no key required for basic endpoints)

## Error Handling

The server includes comprehensive error handling for various scenarios:

- Rate limit exceeded
- Invalid API key
- Network connectivity issues
- Timeout handling
- Malformed responses

Error messages are returned in a clear, human-readable format.

## Prerequisites

- Python 3.12 or higher
- httpx
- mcp

## Contributors

- [berlinbra](https://github.com/berlinbra)
- [zzulanas](https://github.com/zzulanas)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License
This MCP server is licensed under the MIT License. 
This means you are free to use, modify, and distribute the software, subject to the terms and conditions of the MIT License. For more details, please see the LICENSE file in the project repository.

## Trading Bot Integration

This MCP server provides financial data and analysis but does not directly execute trades. For information on integrating with trading platforms like Trading 212 or Alpaca, see [TRADING_INTEGRATION.md](TRADING_INTEGRATION.md).

## Disclaimer

This software is for informational purposes only and does not constitute investment advice. Always conduct your own research and consider the risks before making investment decisions.
