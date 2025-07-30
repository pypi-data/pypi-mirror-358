"""MDS - A simple MCP server for addition operations."""

from .server import create_server
from .tools import add

__version__ = "0.1.0"
__all__ = ["create_server", "add"] 