"""
MCP Server for convertible bond analysis.

This module creates and configures the Model Context Protocol server
using FastMCP framework to expose bond analysis tools.
"""

import argparse
import logging
import sys
from typing import Any, Dict, List

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    # Fallback for basic MCP server
    from mcp.server import Server as FastMCP

from .tools import (
    find_bond_code_by_name,
    get_convertible_bond_realtime_metrics,
    screen_discount_arbitrage_opportunities,
    track_clause_triggers,
    get_upcoming_convertible_bonds,
    monitor_intraday_spread,
    screen_for_special_opportunities,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_server() -> FastMCP:
    """
    Create and configure the MCP server with all bond analysis tools.
    
    Returns:
        FastMCP: Configured server instance
    """
    # Create MCP server instance
    mcp = FastMCP(
        name="BigAMCP Bond Analysis Server",
        description="A comprehensive MCP server for convertible bond analysis using akshare data",
        version="0.1.0"
    )
    
    # Register tool: Find bond by name
    @mcp.tool()
    def find_bond_by_name(bond_name_query: str) -> List[Dict[str, str]]:
        """
        Find convertible bond codes by searching bond names.
        
        Args:
            bond_name_query: Search query for bond name (e.g., "平安", "招商")
            
        Returns:
            List of matching bonds with their codes and names
        """
        return find_bond_code_by_name(bond_name_query)
    
    # Register tool: Get real-time metrics
    @mcp.tool()
    def get_bond_metrics(bond_codes: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Get real-time metrics for specified convertible bonds.
        
        Args:
            bond_codes: List of 6-digit bond codes (e.g., ["113050", "128136"])
            
        Returns:
            Dictionary mapping bond codes to their current metrics including
            bond price, stock price, conversion value, and premium rate
        """
        return get_convertible_bond_realtime_metrics(bond_codes)
    
    # Register tool: Screen discount arbitrage opportunities
    @mcp.tool()
    def screen_discount_arbitrage(min_discount_rate: float = -0.01) -> List[Dict[str, Any]]:
        """
        Screen for convertible bonds with discount arbitrage opportunities.
        
        Args:
            min_discount_rate: Minimum discount rate threshold (negative for discount)
            
        Returns:
            List of bonds with discount arbitrage opportunities
        """
        return screen_discount_arbitrage_opportunities(min_discount_rate)
    
    # Register tool: Track clause triggers
    @mcp.tool()
    def track_bond_clause_triggers(bond_code: str) -> Dict[str, Any]:
        """
        Track redemption and put clause trigger status for a specific bond.
        
        Args:
            bond_code: 6-digit bond code to analyze
            
        Returns:
            Analysis of clause trigger conditions based on recent stock performance
        """
        return track_clause_triggers(bond_code)
    
    # Register tool: Get upcoming bonds
    @mcp.tool()
    def get_upcoming_bonds(days_ahead: int = 30) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get upcoming convertible bond issuances and subscription opportunities.
        
        Args:
            days_ahead: Number of days to look ahead (default: 30)
            
        Returns:
            Dictionary with categorized upcoming bond events
        """
        return get_upcoming_convertible_bonds(days_ahead)
    
    # Register tool: Monitor intraday spread
    @mcp.tool()
    def monitor_bond_spread(bond_code: str) -> Dict[str, Any]:
        """
        Monitor intraday spread for a specific convertible bond.
        
        Args:
            bond_code: 6-digit bond code to monitor
            
        Returns:
            Current spread and pricing metrics for the bond
        """
        return monitor_intraday_spread(bond_code)
    
    # Register tool: Screen special opportunities
    @mcp.tool()
    def screen_special_opportunities(
        discount_threshold: float = -0.01,
        trigger_proximity_threshold: float = 0.8,
        redemption_clause_days: int = 15,
        put_clause_days: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Screen for special arbitrage opportunities combining discount and clause triggers.
        
        Args:
            discount_threshold: Discount rate threshold for arbitrage opportunities
            trigger_proximity_threshold: Proximity threshold for clause triggers (0.8 = 80%)
            redemption_clause_days: Days required for redemption clause (default: 15)
            put_clause_days: Days required for put clause (default: 30)
            
        Returns:
            List of bonds with special arbitrage opportunities
        """
        return screen_for_special_opportunities(
            discount_threshold,
            trigger_proximity_threshold,
            redemption_clause_days,
            put_clause_days
        )
    
    return mcp


def main():
    """
    Main entry point for the MCP server.
    """
    parser = argparse.ArgumentParser(description="BigAMCP Bond Analysis MCP Server")
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse"],
        default="stdio",
        help="Transport method for MCP communication"
    )
    parser.add_argument(
        "--host",
        default="localhost",
        help="Host for SSE transport (default: localhost)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port for SSE transport (default: 8000)"
    )
    
    args = parser.parse_args()
    
    # Create and configure the server
    server = create_server()
    
    try:
        if args.transport == "stdio":
            logger.info("Starting MCP server with stdio transport")
            server.run(transport="stdio")
        elif args.transport == "sse":
            logger.info(f"Starting MCP server with SSE transport on {args.host}:{args.port}")
            server.run(transport="sse", host=args.host, port=args.port)
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
