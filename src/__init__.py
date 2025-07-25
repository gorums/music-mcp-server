"""
Music Collection MCP Server Package

This package provides MCP server functionality for managing and analyzing
local music collections with comprehensive metadata management, collection
analytics, and intelligent music discovery features.
"""

# Package metadata
__version__ = "1.0.0"
__author__ = "Music MCP Server"
__description__ = "MCP server for music collection management and analysis"

# Main exports
from .mcp_server import create_server, mcp

# Core module exports
from . import (
    config,
    core,
    exceptions,
    models,
    mcp_server,
)

__all__ = [
    # Package metadata
    "__version__",
    "__author__",
    "__description__",
    
    # Main server functionality
    "create_server",
    "mcp",
    
    # Core modules
    "config",
    "core",
    "exceptions",
    "models",
    "mcp_server",
] 