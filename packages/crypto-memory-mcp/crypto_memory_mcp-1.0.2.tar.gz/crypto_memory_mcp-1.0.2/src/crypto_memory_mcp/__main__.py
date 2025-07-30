#!/usr/bin/env python3

import asyncio
from crypto_memory_mcp.server import main

def cli_main():
    """CLI entry point"""
    asyncio.run(main())

if __name__ == "__main__":
    cli_main()
