"""HTTP/SSE transport entrypoint for Railway deployment."""
from __future__ import annotations

import os
import logging

import uvicorn
from mcp.server.sse import SseServerTransport
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.routing import Mount, Route

from .mcp_server import server

logger = logging.getLogger("crawl4ai_mcp.http")

sse = SseServerTransport("/messages/")


async def handle_sse(request: Request):
    async with sse.connect_sse(request.scope, request.receive, request._send) as streams:
        await server.run(
            streams[0],
            streams[1],
            InitializationOptions(
                server_name="crawl4ai-mcp",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


app = Starlette(
    routes=[
        Route("/sse", endpoint=handle_sse),
        Mount("/messages/", app=sse.handle_post_message),
    ]
)


def main() -> None:
    port = int(os.getenv("PORT", "8000"))
    logger.info("starting HTTP/SSE server on port %d", port)
    uvicorn.run(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
