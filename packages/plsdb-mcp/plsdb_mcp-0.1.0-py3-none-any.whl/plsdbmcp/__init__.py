"""
PLSDB MCP Server

Model Context Protocol server for interacting with the PLSDB (Plasmid Database) API.
This server provides tools to search, filter, and retrieve plasmid data from PLSDB.
"""

__version__ = "0.1.0"
__author__ = "PLSDB MCP Team"

from .main import cli_main

__all__ = ["cli_main"] 