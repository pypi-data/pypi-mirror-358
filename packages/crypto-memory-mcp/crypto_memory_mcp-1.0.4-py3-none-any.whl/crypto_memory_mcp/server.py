#!/usr/bin/env python3

import asyncio
import json
import os
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union

from dotenv import load_dotenv
from mem0 import Memory
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool
from pydantic import BaseModel, Field

# Load environment variables
load_dotenv()


class CryptoAnalysis(BaseModel):
    """Model for cryptocurrency analysis data"""
    symbol: str
    analysis_type: str
    timestamp: datetime
    data: Dict[str, Any]
    summary: str
    metadata: Optional[Dict[str, Any]] = None


class CryptoMemoryServer:
    """Memory-Enhanced MCP Server for Cryptocurrency Analysis"""
    
    def __init__(self):
        self.server = Server("crypto-memory-mcp")
        self.memory = None
        self.user_id = "crypto_analyst"  # Default user ID for memory isolation
        
        # Register tools
        self._register_tools()
        
    def _register_tools(self):
        """Register all available tools"""
        
        # Memory storage tools
        @self.server.call_tool()
        async def store_crypto_analysis(
            symbol: str,
            analysis_type: str,
            data: str,
            summary: str,
            metadata: Optional[str] = None
        ) -> List[TextContent]:
            """
            Store cryptocurrency analysis in persistent memory.
            
            Args:
                symbol: Cryptocurrency symbol (e.g., BTCUSDT)
                analysis_type: Type of analysis (technical, fundamental, price_action, etc.)
                data: JSON string containing analysis data
                summary: Brief summary of the analysis
                metadata: Optional JSON string with additional metadata
            """
            try:
                # Parse JSON data
                parsed_data = json.loads(data)
                parsed_metadata = json.loads(metadata) if metadata else {}
                
                # Create analysis object
                analysis = CryptoAnalysis(
                    symbol=symbol.upper(),
                    analysis_type=analysis_type,
                    timestamp=datetime.now(timezone.utc),
                    data=parsed_data,
                    summary=summary,
                    metadata=parsed_metadata
                )
                
                # Store in memory with rich context
                memory_text = f"""
                Cryptocurrency Analysis for {symbol.upper()}:
                Type: {analysis_type}
                Summary: {summary}
                Timestamp: {analysis.timestamp.isoformat()}
                
                Analysis Data: {json.dumps(parsed_data, indent=2)}
                """
                
                if parsed_metadata:
                    memory_text += f"\nMetadata: {json.dumps(parsed_metadata, indent=2)}"
                
                # Add memory with metadata
                memory_metadata = {
                    "symbol": symbol.upper(),
                    "analysis_type": analysis_type,
                    "timestamp": analysis.timestamp.isoformat(),
                    "category": "crypto_analysis"
                }
                memory_metadata.update(parsed_metadata)
                
                await self._ensure_memory_initialized()
                result = self.memory.add(
                    memory_text,
                    user_id=self.user_id,
                    metadata=memory_metadata
                )
                
                # Handle mem0 result format
                memory_id = "unknown"
                if isinstance(result, dict) and 'results' in result:
                    results_list = result.get('results', [])
                    if results_list and len(results_list) > 0:
                        memory_id = results_list[0].get('id', 'unknown')
                
                return [TextContent(
                    type="text",
                    text=f"✅ Successfully stored {analysis_type} analysis for {symbol.upper()}. Memory ID: {memory_id}"
                )]
                
            except json.JSONDecodeError as e:
                return [TextContent(
                    type="text",
                    text=f"❌ Error parsing JSON data: {str(e)}"
                )]
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"❌ Error storing analysis: {str(e)}"
                )]

        @self.server.call_tool()
        async def retrieve_crypto_analysis(
            symbol: Optional[str] = None,
            analysis_type: Optional[str] = None,
            limit: int = 10
        ) -> List[TextContent]:
            """
            Retrieve stored cryptocurrency analysis from memory.
            
            Args:
                symbol: Optional cryptocurrency symbol to filter by
                analysis_type: Optional analysis type to filter by
                limit: Maximum number of results to return (default: 10)
            """
            try:
                await self._ensure_memory_initialized()
                
                # Build search query
                query_parts = []
                if symbol:
                    query_parts.append(f"cryptocurrency {symbol.upper()}")
                if analysis_type:
                    query_parts.append(f"{analysis_type} analysis")
                
                search_query = " ".join(query_parts) if query_parts else "cryptocurrency analysis"
                
                # Search memories
                memories_result = self.memory.search(
                    query=search_query,
                    user_id=self.user_id,
                    limit=limit
                )
                
                # Handle mem0 result format
                memories = []
                if isinstance(memories_result, dict) and 'results' in memories_result:
                    memories = memories_result.get('results', [])
                
                if not memories:
                    return [TextContent(
                        type="text",
                        text="📭 No analysis found matching your criteria."
                    )]
                
                # Format results
                results = []
                for i, memory in enumerate(memories, 1):
                    # Handle both dict and string memory formats
                    if isinstance(memory, dict):
                        metadata = memory.get('metadata', {})
                        score = memory.get('score', 0)
                        content = memory.get('memory', memory.get('text', 'No content'))
                    else:
                        # If memory is a string
                        metadata = {}
                        score = 0
                        content = str(memory)
                    
                    result_text = f"""
🔍 **Analysis #{i}** (Relevance: {score:.2f})
📊 Symbol: {metadata.get('symbol', 'Unknown')}
📈 Type: {metadata.get('analysis_type', 'Unknown')}
📅 Date: {metadata.get('timestamp', 'Unknown')}

{content[:500]}...

---
"""
                    results.append(result_text)
                
                return [TextContent(
                    type="text",
                    text=f"📊 Found {len(memories)} analysis results:\n\n" + "\n".join(results)
                )]
                
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"❌ Error retrieving analysis: {str(e)}"
                )]

        @self.server.call_tool()
        async def compare_crypto_symbols(
            symbols: str,
            analysis_type: Optional[str] = None
        ) -> List[TextContent]:
            """
            Compare analysis across multiple cryptocurrency symbols.
            
            Args:
                symbols: Comma-separated list of symbols to compare (e.g., "BTCUSDT,ETHUSDT,ADAUSDT")
                analysis_type: Optional analysis type to focus on
            """
            try:
                await self._ensure_memory_initialized()
                
                symbol_list = [s.strip().upper() for s in symbols.split(',')]
                comparisons = {}
                
                for symbol in symbol_list:
                    query = f"cryptocurrency {symbol}"
                    if analysis_type:
                        query += f" {analysis_type} analysis"
                    
                    memories_result = self.memory.search(
                        query=query,
                        user_id=self.user_id,
                        limit=3  # Get top 3 most relevant for each symbol
                    )
                    
                    # Handle mem0 result format
                    memories = []
                    if isinstance(memories_result, dict) and 'results' in memories_result:
                        memories = memories_result.get('results', [])
                    
                    comparisons[symbol] = memories
                
                # Format comparison
                comparison_text = f"🔄 **Comparison Analysis for: {', '.join(symbol_list)}**\n\n"
                
                for symbol, memories in comparisons.items():
                    comparison_text += f"## 📊 {symbol}\n"
                    
                    if not memories:
                        comparison_text += "❌ No analysis data found.\n\n"
                        continue
                    
                    for memory in memories:
                        # Handle both dict and string memory formats
                        if isinstance(memory, dict):
                            metadata = memory.get('metadata', {})
                            content = memory.get('memory', memory.get('text', 'No content'))
                            timestamp = metadata.get('timestamp', 'Unknown date')
                            analysis_type_display = metadata.get('analysis_type', 'Analysis')
                        else:
                            timestamp = 'Unknown date'
                            analysis_type_display = 'Analysis'
                            content = str(memory)
                        
                        comparison_text += f"""
**{analysis_type_display}** ({timestamp})
{content[:300]}...

"""
                    comparison_text += "---\n\n"
                
                return [TextContent(
                    type="text",
                    text=comparison_text
                )]
                
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"❌ Error comparing symbols: {str(e)}"
                )]

        @self.server.call_tool()
        async def search_crypto_insights(
            query: str,
            limit: int = 5
        ) -> List[TextContent]:
            """
            Search for specific insights across all stored cryptocurrency analysis.
            
            Args:
                query: Natural language search query (e.g., "bullish trends", "resistance levels")
                limit: Maximum number of results to return
            """
            try:
                await self._ensure_memory_initialized()
                
                memories_result = self.memory.search(
                    query=f"cryptocurrency {query}",
                    user_id=self.user_id,
                    limit=limit
                )
                
                # Handle mem0 result format
                memories = []
                if isinstance(memories_result, dict) and 'results' in memories_result:
                    memories = memories_result.get('results', [])
                
                if not memories:
                    return [TextContent(
                        type="text",
                        text=f"🔍 No insights found for query: '{query}'"
                    )]
                
                insights_text = f"🧠 **Insights for: '{query}'**\n\n"
                
                for i, memory in enumerate(memories, 1):
                    # Handle both dict and string memory formats
                    if isinstance(memory, dict):
                        metadata = memory.get('metadata', {})
                        score = memory.get('score', 0)
                        content = memory.get('memory', memory.get('text', 'No content available'))
                    else:
                        metadata = {}
                        score = 0
                        content = str(memory)
                    
                    insights_text += f"""
**Insight #{i}** (Relevance: {score:.2f})
🪙 Symbol: {metadata.get('symbol', 'Unknown')}
📊 Type: {metadata.get('analysis_type', 'Unknown')}
📅 Date: {metadata.get('timestamp', 'Unknown')}

{content[:400]}...

---

"""
                
                return [TextContent(
                    type="text",
                    text=insights_text
                )]
                
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"❌ Error searching insights: {str(e)}"
                )]

        @self.server.call_tool()
        async def get_memory_stats() -> List[TextContent]:
            """Get statistics about stored cryptocurrency analysis memories."""
            try:
                await self._ensure_memory_initialized()
                
                # Get all crypto analysis memories
                all_memories_result = self.memory.search(
                    query="cryptocurrency analysis",
                    user_id=self.user_id,
                    limit=1000  # Large limit to get all
                )
                
                # Handle mem0 result format
                all_memories = []
                if isinstance(all_memories_result, dict) and 'results' in all_memories_result:
                    all_memories = all_memories_result.get('results', [])
                
                # Analyze statistics
                total_analyses = len(all_memories)
                symbols = set()
                analysis_types = {}
                dates = []
                
                for memory in all_memories:
                    # Handle both dict and string memory formats
                    if isinstance(memory, dict):
                        metadata = memory.get('metadata', {})
                        
                        if 'symbol' in metadata:
                            symbols.add(metadata['symbol'])
                        
                        if 'analysis_type' in metadata:
                            analysis_type = metadata['analysis_type']
                            analysis_types[analysis_type] = analysis_types.get(analysis_type, 0) + 1
                        
                        if 'timestamp' in metadata:
                            dates.append(metadata['timestamp'])
                
                # Format statistics
                stats_text = f"""
📊 **Cryptocurrency Analysis Memory Statistics**

🔢 **Total Analyses**: {total_analyses}
🪙 **Unique Symbols**: {len(symbols)}
📈 **Analysis Types**: {len(analysis_types)}

**Symbols Tracked**: {', '.join(sorted(symbols)) if symbols else 'None'}

**Analysis Type Breakdown**:
"""
                
                for analysis_type, count in sorted(analysis_types.items()):
                    stats_text += f"  • {analysis_type}: {count}\n"
                
                if dates:
                    latest_date = max(dates)
                    oldest_date = min(dates)
                    stats_text += f"""
📅 **Date Range**: 
  • Latest: {latest_date}
  • Oldest: {oldest_date}
"""
                
                return [TextContent(
                    type="text",
                    text=stats_text
                )]
                
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"❌ Error getting memory stats: {str(e)}"
                )]

        @self.server.call_tool()
        async def delete_crypto_analysis(
            symbol: str,
            analysis_type: Optional[str] = None
        ) -> List[TextContent]:
            """
            Delete stored cryptocurrency analysis for a specific symbol.
            
            Args:
                symbol: Cryptocurrency symbol to delete analysis for
                analysis_type: Optional specific analysis type to delete
            """
            try:
                await self._ensure_memory_initialized()
                
                # Search for memories to delete
                query = f"cryptocurrency {symbol.upper()}"
                if analysis_type:
                    query += f" {analysis_type} analysis"
                
                memories = self.memory.search(
                    query=query,
                    user_id=self.user_id,
                    limit=100
                )
                
                deleted_count = 0
                for memory in memories:
                    metadata = memory.get('metadata', {})
                    if metadata.get('symbol') == symbol.upper():
                        if not analysis_type or metadata.get('analysis_type') == analysis_type:
                            # Delete this memory
                            memory_id = memory.get('id')
                            if memory_id:
                                self.memory.delete(memory_id)
                                deleted_count += 1
                
                return [TextContent(
                    type="text",
                    text=f"🗑️ Deleted {deleted_count} analysis entries for {symbol.upper()}" +
                         (f" ({analysis_type})" if analysis_type else "")
                )]
                
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"❌ Error deleting analysis: {str(e)}"
                )]

    async def _ensure_memory_initialized(self):
        """Ensure memory system is initialized"""
        if self.memory is None:
            # Initialize mem0 with default configuration
            # It will use OPENAI_API_KEY from environment automatically
            try:
                self.memory = Memory()
                print("✅ Memory system initialized with OpenAI (from environment)")
            except Exception as e:
                print(f"❌ Failed to initialize memory system: {e}")
                # Create a fallback that still works
                self.memory = None
                raise e

    async def run(self):
        """Run the MCP server"""
        
        # Set server info
        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            """List available tools"""
            return [
                Tool(
                    name="store_crypto_analysis",
                    description="Store cryptocurrency analysis in persistent memory for later retrieval",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "symbol": {
                                "type": "string",
                                "description": "Cryptocurrency symbol (e.g., BTCUSDT)"
                            },
                            "analysis_type": {
                                "type": "string", 
                                "description": "Type of analysis (technical, fundamental, price_action, sentiment, etc.)"
                            },
                            "data": {
                                "type": "string",
                                "description": "JSON string containing analysis data"
                            },
                            "summary": {
                                "type": "string",
                                "description": "Brief summary of the analysis"
                            },
                            "metadata": {
                                "type": "string",
                                "description": "Optional JSON string with additional metadata"
                            }
                        },
                        "required": ["symbol", "analysis_type", "data", "summary"]
                    }
                ),
                Tool(
                    name="retrieve_crypto_analysis",
                    description="Retrieve stored cryptocurrency analysis from memory",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "symbol": {
                                "type": "string",
                                "description": "Optional cryptocurrency symbol to filter by"
                            },
                            "analysis_type": {
                                "type": "string",
                                "description": "Optional analysis type to filter by"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of results to return",
                                "default": 10
                            }
                        }
                    }
                ),
                Tool(
                    name="compare_crypto_symbols",
                    description="Compare analysis across multiple cryptocurrency symbols",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "symbols": {
                                "type": "string",
                                "description": "Comma-separated list of symbols to compare"
                            },
                            "analysis_type": {
                                "type": "string",
                                "description": "Optional analysis type to focus on"
                            }
                        },
                        "required": ["symbols"]
                    }
                ),
                Tool(
                    name="search_crypto_insights",
                    description="Search for specific insights across all stored cryptocurrency analysis",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Natural language search query"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of results to return",
                                "default": 5
                            }
                        },
                        "required": ["query"]
                    }
                ),
                Tool(
                    name="get_memory_stats",
                    description="Get statistics about stored cryptocurrency analysis memories",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                Tool(
                    name="delete_crypto_analysis",
                    description="Delete stored cryptocurrency analysis for a specific symbol",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "symbol": {
                                "type": "string",
                                "description": "Cryptocurrency symbol to delete analysis for"
                            },
                            "analysis_type": {
                                "type": "string",
                                "description": "Optional specific analysis type to delete"
                            }
                        },
                        "required": ["symbol"]
                    }
                )
            ]
        
        # Initialize and run server
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="crypto-memory-mcp",
                    server_version="1.0.3",
                    capabilities=self.server.get_capabilities(
                        notification_options=None,
                        experimental_capabilities={}
                    )
                )
            )


async def main():
    """Main entry point"""
    server = CryptoMemoryServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
