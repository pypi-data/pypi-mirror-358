import logging
import os

import click
import uvicorn
from fastapi import FastAPI


@click.command()
def run_app():
    """Main function to run the MCP server.

    If the environment variable MCP_ENVIRONMENT is set to PRODUCTION, it will run the FastAPI app with streamable HTTP
    for the MCP server. Otherwise, it will run the MCP server via stdio.

    In production, the app will be mounted at /mcp in the FastAPI app and will be accessible at the root URL.
    The port is set via the PORT environment variable, defaulting to 8000 if not set.
    """
    logger = logging.getLogger(__name__)

    from biocontext_server.app import app

    if isinstance(app, FastAPI):
        logger.info("Starting FastAPI app with Uvicorn in PRODUCTION mode.")
        uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
    else:
        logger.info("Starting MCP server via stdio (non-PRODUCTION mode).")
        app.run(transport="stdio")


if __name__ == "__main__":
    run_app()
