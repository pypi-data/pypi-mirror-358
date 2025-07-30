# BigAMCP Bond Analysis

A comprehensive Model Context Protocol (MCP) server for convertible bond analysis using akshare data.

## Features

This MCP server provides the following tools for convertible bond analysis:

### 🔍 Bond Discovery
- **find_bond_by_name**: Search for convertible bonds by name with fuzzy matching
- **get_bond_metrics**: Get real-time metrics for specific bonds

### 📊 Market Analysis
- **screen_discount_arbitrage**: Find bonds with discount arbitrage opportunities
- **screen_special_opportunities**: Advanced screening combining discount and clause triggers
- **get_upcoming_bonds**: Discover upcoming bond issuances and subscription opportunities

### ⚡ Real-time Monitoring
- **monitor_bond_spread**: Monitor intraday spread for specific bonds
- **track_bond_clause_triggers**: Track redemption and put clause trigger status

## Installation

### Using uvx (Recommended)

```bash
uvx bigamcp-bond-analysis
```

### Using pip

```bash
pip install bigamcp-bond-analysis
```

## Usage

### As MCP Server

Start the server with stdio transport (default):

```bash
bigamcp-bond-analysis
```

Or with SSE transport:

```bash
bigamcp-bond-analysis --transport sse --host localhost --port 8000
```

### With MCP Inspector

Test the server using MCP Inspector:

```bash
npx @modelcontextprotocol/inspector uvx bigamcp-bond-analysis
```

### Configuration for Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "bigamcp-bond-analysis": {
      "command": "uvx",
      "args": ["bigamcp-bond-analysis"]
    }
  }
}
```

## Available Tools

### find_bond_by_name
Search for convertible bonds by name.

**Parameters:**
- `bond_name_query` (string): Search query for bond name

**Example:**
```json
{
  "bond_name_query": "平安"
}
```

### get_bond_metrics
Get real-time metrics for specified bonds.

**Parameters:**
- `bond_codes` (array): List of 6-digit bond codes

**Example:**
```json
{
  "bond_codes": ["113050", "128136"]
}
```

### screen_discount_arbitrage
Screen for bonds with discount arbitrage opportunities.

**Parameters:**
- `min_discount_rate` (number, optional): Minimum discount rate threshold (default: -0.01)

### track_bond_clause_triggers
Track clause trigger status for a specific bond.

**Parameters:**
- `bond_code` (string): 6-digit bond code

### get_upcoming_bonds
Get upcoming bond events.

**Parameters:**
- `days_ahead` (number, optional): Number of days to look ahead (default: 30)

### monitor_bond_spread
Monitor intraday spread for a bond.

**Parameters:**
- `bond_code` (string): 6-digit bond code

### screen_special_opportunities
Advanced screening for special arbitrage opportunities.

**Parameters:**
- `discount_threshold` (number, optional): Discount rate threshold (default: -0.01)
- `trigger_proximity_threshold` (number, optional): Proximity threshold for triggers (default: 0.8)
- `redemption_clause_days` (number, optional): Days for redemption clause (default: 15)
- `put_clause_days` (number, optional): Days for put clause (default: 30)

## Data Source

This server uses [akshare](https://github.com/akfamily/akshare) library to fetch real-time convertible bond data from various Chinese financial data sources.

## Requirements

- Python 3.10+
- Internet connection for data fetching

## Development

### Setup Development Environment

```bash
git clone <repository-url>
cd bigamcp-bond-analysis
uv sync --dev
```

### Run Tests

```bash
uv run pytest
```

### Code Formatting

```bash
uv run black src tests
uv run ruff check src tests
```

### Type Checking

```bash
uv run mypy src
```

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

If you encounter any issues or have questions, please open an issue on GitHub.