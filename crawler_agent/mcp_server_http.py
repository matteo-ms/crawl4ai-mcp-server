"""HTTP/SSE transport entrypoint for Railway deployment."""
from __future__ import annotations

import os
import logging

import uvicorn
from mcp.server.sse import SseServerTransport
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions
from starlette.responses import Response

from .mcp_server import server

logger = logging.getLogger("crawl4ai_mcp.http")

_init_options = InitializationOptions(
    server_name="crawl4ai-mcp",
    server_version="0.1.0",
    capabilities=server.get_capabilities(
        notification_options=NotificationOptions(),
        experimental_capabilities={},
    ),
)

sse = SseServerTransport("/messages/")


class App:
    """Minimal ASGI router — no trailing-slash redirects."""

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return
        path = scope.get("path", "")
        if path == "/sse":
            async with sse.connect_sse(scope, receive, send) as streams:
                await server.run(streams[0], streams[1], _init_options)
        elif path.startswith("/messages/"):
            await sse.handle_post_message(scope, receive, send)
        else:
            await Response(status_code=404)(scope, receive, send)


app = App()


def main() -> None:
    port = int(os.getenv("PORT", "8000"))
    logger.info("starting HTTP/SSE server on port %d", port)
    uvicorn.run("crawler_agent.mcp_server_http:app", host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
