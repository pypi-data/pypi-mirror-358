"""
Crypto Memory MCP Server

A Memory-Enhanced MCP Server for Cryptocurrency Analysis using mem0.
Solves the context window limitation problem when analyzing multiple cryptocurrencies.
"""

__version__ = "1.0.0"
__author__ = "Crypto Memory MCP"

from .server import CryptoMemoryServer, main

__all__ = ["CryptoMemoryServer", "main"]
