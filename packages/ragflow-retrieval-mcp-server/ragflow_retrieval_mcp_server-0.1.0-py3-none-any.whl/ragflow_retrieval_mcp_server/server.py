import asyncio
import logging
import os
from typing import Optional
import aiohttp
from mcp.server import Server
from mcp.types import Tool, TextContent
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.routing import Mount, Route


class Config:
    def __init__(self):
        self.ragflow_api_key: Optional[str] = os.getenv("RAGFLOW_API_KEY", 'Not set')
        self.ragflow_dataset_id: Optional[str] = os.getenv("RAGFLOW_DATASET_ID", 'Not set')
        self.ragflow_base_url: str = os.getenv("RAGFLOW_BASE_URL", "http://127.0.0.1:80")
        self.ragflow_top_k: int = int(os.getenv("RAGFLOW_TOP_K", 10))
        self.ragflow_similarity_threshold: float = float(os.getenv("RAGFLOW_SIMILARITY_THRESHOLD", 0.5))
        self.ragflow_timeout: int = int(os.getenv("RAGFLOW_TIMEOUT", 60))

        self.server_host: str = os.getenv("SERVER_HOST", "0.0.0.0")
        self.server_port: int = int(os.getenv("SERVER_PORT", 8002))

        if not self.ragflow_base_url.startswith(("http://", "https://")):
            raise ValueError("Invalid BASE_URL format")


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ragflow-retrieval-mcp-server")

# Initialize configuration
try:
    config = Config()
except ValueError as e:
    logger.critical(f"Configuration error: {str(e)}")
    exit(1)

# Initialize MCP server
sse = SseServerTransport("/messages/")
app = Server("ragflow_retrieval_mcp_server")


@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="retrieval",
            description="Retrieve content from knowledge base",
            inputSchema={
                "type": "object",
                "properties": {
                    "keyword": {
                        "type": "string",
                        "description": "Search keyword"
                    }
                },
                "required": ["keyword"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name != "retrieval":
        raise ValueError(f"Unknown tool: {name}")

    if not config.ragflow_api_key or not config.ragflow_dataset_id:
        return [TextContent(type="text", text="Service configuration error")]

    keyword = arguments.get("keyword", "").strip()
    if not keyword:
        return [TextContent(type="text", text="Keyword parameter cannot be empty")]

    url = f"{config.ragflow_base_url}/api/v1/retrieval"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {config.ragflow_api_key}"
    }
    payload = {
        "question": keyword,
        "dataset_ids": [config.ragflow_dataset_id],
        "keyword": True,
        "top_k": config.ragflow_top_k,
        "similarity_threshold": config.ragflow_similarity_threshold
    }

    try:
        async with aiohttp.ClientSession() as session:
            # Call RAGFlow REST API
            async with session.post(
                url,
                json=payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=config.ragflow_timeout)
            ) as response:
                response.raise_for_status()
                data = await response.json()

                # Process response chunks
                contents = []
                for chunk in data.get("data", {}).get("chunks", []):
                    if content := chunk.get("content", ""):
                        contents.append(TextContent(type="text", text=content))

                # Return top 5 most relevant results
                return contents[:5]

    except aiohttp.ClientError as e:
        logger.error(f"API request failed: {str(e)}")
        return [TextContent(type="text", text="Retrieval service temporary unavailable")]
    except Exception as e:
        logger.error(f"Processing error: {type(e).__name__}", exc_info=True)
        return [TextContent(type="text", text="Error processing request")]


async def handle_sse(request):
    async with sse.connect_sse(
        request.scope, request.receive, request._send
    ) as streams:
        await app.run(
            streams[0], streams[1], app.create_initialization_options()
        )


def main_sse():
    """Start sse mode server"""

    logger.info("Starting RAGFlow MCP service...")
    logger.info(f"Configured dataset ID: {config.ragflow_dataset_id}")

    starlette_app = Starlette(
        debug=False,
        routes=[
            Route("/sse", endpoint=handle_sse),
            Mount("/messages/", app=sse.handle_post_message),
        ],
    )

    import uvicorn
    uvicorn.run(starlette_app,
                host=config.server_host,
                port=config.server_port
                )


async def main():
    """Start stdio mode server"""
    from mcp.server.stdio import stdio_server

    logger.info("Starting RAGFlow retrieval MCP service...")
    logger.info(f"Configured dataset ID: {config.ragflow_dataset_id}")

    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
