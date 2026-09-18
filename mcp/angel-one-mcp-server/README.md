# Angel One MCP Server

Angel One Limited (formerly Angel Broking Limited) is India's leading stockbroker firm established in 1996, serving over 24.7 million clients across major Indian stock exchanges including BSE and NSE. This server provides access to Indian equity markets, commodities, and derivatives trading.

A Model Context Protocol (MCP) server that provides comprehensive trading and market data functionality for Angel One through their SmartAPI.

## Features

### Portfolio Management

- View stock holdings and investment portfolio
- Get comprehensive family account holdings
- Check current trading positions
- Access Risk Management System (RMS) limits

### Trading Operations

- Place buy/sell orders (market, limit, stop-loss)
- Modify existing orders
- Cancel orders
- View order book and trade history
- Create GTT (Good Till Triggered) rules

### Market Data

- Real-time Last Traded Price (LTP)
- Historical candlestick (OHLC) data
- Search for stocks and instruments
- Top gainers/losers analysis
- Put-Call Ratio (PCR) for market sentiment

### Advanced Features

- Option Greeks calculation
- Position conversion
- Brokerage estimation
- Automated authentication with TOTP
- Comprehensive error handling
- Safety controls and dry-run mode

## Installation

### Development Installation (Current)

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/angel-one-mcp-server.git
cd angel-one-mcp-server

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .
```

### PyPI Installation (Coming Soon)

```bash
pip install angel-one-mcp
```

### Read-only market-data pacing

The MCP serializes Angel One provider calls through one in-process queue. The
configured default is one request every 1.5 seconds, with a 60-second cache for
quotes and a 24-hour cache for symbol resolution. Override locally with
`ANGEL_ONE_MIN_REQUEST_INTERVAL` and `ANGEL_ONE_QUOTE_CACHE_TTL` only when the
provider limits and workload justify it. Provider rate-limit errors are not
retried in parallel; callers should allow the bounded error to surface.

## Configuration

You can configure your Angel One credentials using either of these approaches:

### Option 1: Environment Variables (Recommended)

Create a `.env` file in your project directory:

```bash
ANGEL_ONE_API_KEY=your_api_key
ANGEL_ONE_CLIENT_CODE=your_client_code
ANGEL_ONE_PASSWORD=your_password
ANGEL_ONE_TOTP_SECRET=your_totp_secret
MAX_ORDER_QUANTITY=10000
DRY_RUN_MODE=false
```

Then configure Claude Desktop (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "angel-one-trading": {
      "command": "python",
      "args": ["-m", "angel_one_mcp.server"]
    }
  }
}
```

### Option 2: Direct Configuration

Configure credentials directly in Claude Desktop (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "angel-one-trading": {
      "command": "python",
      "args": ["-m", "angel_one_mcp.server"],
      "env": {
        "ANGEL_ONE_API_KEY": "your_api_key",
        "ANGEL_ONE_CLIENT_CODE": "your_client_code", 
        "ANGEL_ONE_PASSWORD": "your_password",
        "ANGEL_ONE_TOTP_SECRET": "your_totp_secret"
      }
    }
  }
}
```

**Note:** Option 1 is recommended as it keeps sensitive credentials separate from configuration files.

## Usage Examples

### Portfolio Management

- "Show my current holdings"
- "What's my available margin?"
- "Display my open positions"

### Trading

- "Buy 100 shares of RELIANCE at market price"
- "Place a limit order to sell 50 TCS at ₹3500"
- "Cancel order ID 12345"

### Market Data

- "What's the current price of NIFTY?"
- "Show me top gainers today"
- "Get historical data for SBIN"

## Security Features

- Automatic TOTP-based authentication
- Configurable order quantity limits
- Dry-run mode for testing
- Comprehensive error handling
- No credential storage in memory

## Requirements

- Python 3.8+
- Angel One SmartAPI account
- Valid API credentials and TOTP setup

## License

MIT License
