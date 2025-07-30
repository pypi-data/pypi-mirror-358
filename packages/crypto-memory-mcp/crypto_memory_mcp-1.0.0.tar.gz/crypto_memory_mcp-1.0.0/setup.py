#!/usr/bin/env python3

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="crypto-memory-mcp",
    version="1.0.0",
    author="Crypto Memory MCP",
    description="A Memory-Enhanced MCP Server for Cryptocurrency Analysis using mem0",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/crypto-memory-mcp",
    project_urls={
        "Bug Tracker": "https://github.com/crypto-memory-mcp/issues",
        "Repository": "https://github.com/crypto-memory-mcp.git",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Office/Business :: Financial :: Investment",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.8",
    install_requires=[
        "mcp>=1.0.0",
        "mem0ai>=0.1.0", 
        "pydantic>=2.0.0",
        "aiohttp>=3.8.0",
        "python-dotenv>=1.0.0",
    ],
    entry_points={
        "console_scripts": [
            "crypto-memory-mcp=crypto_memory_mcp.__main__:cli_main",
        ],
    },
    keywords="mcp cryptocurrency memory analysis mem0 model-context-protocol binance",
)
