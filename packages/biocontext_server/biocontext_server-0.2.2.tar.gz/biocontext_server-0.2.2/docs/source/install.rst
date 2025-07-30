
.. _install:


============
Installation
============

.. highlight:: console
.. _setuptools: https://pypi.org/project/setuptools/


For installation of this package you need to have Python 3.8 or newer installed. You can install ``biocontext_server`` with ``pip``::

    pip install biocontext_server

Or ``uv``::

    uv add biocontext_server

.. _selfhosting:

Self-hosting
-----------

Install the package as shown above or the latest version of the repository::

    git clone https://github.com/biocontext-ai/core-mcp-server.git
    cd core-mcp-server

There are several ways to run BioContextAI Core:

1. Remote server production use cases (gunicorn with multiple uvicorn workers)::

    export MCP_ENVIRONMENT=PRODUCTION
    export PYTHONPATH=.
    export PORT=8000
    uv sync
    uv run gunicorn "biocontext_server:app" -c gunicorn_conf.py # Assuming you have a gunicorn configuration file

For public deployments, we recommend protecting your server with Cloudflare, fail2ban, an Nginx reverse proxy and ensuring availability through management with a process manager, e.g., systemd and disallowing all ports except ssh, http and https with ufw.

2. Locally, with streamable HTTP::

    uv build
    export MCP_ENVIRONMENT=PRODUCTION
    export PORT=8000
    biocontext_server

3. Locally, with stdio transport::

    uv build
    export MCP_ENVIRONMENT=DEVELOPMENT
    biocontext_server

4. Locally, with Claude Desktop (``claude_desktop_config.json``)::

    {
      "mcpServers": {
        // add uvx example once the package is published
      }
    }

Don't forget to restart Claude to apply the changes.

5. Locally, with your coding agents in VS Code (``.vscode/mcp.json``) or Cursor (``.cursor/mcp.json``) or WindSurf (``.codeium/windsurf/mcp_config.json``).

6. Locally, with your own agents:

- Follow the ``FastMCP`` `setup guide <https://gofastmcp.com/getting-started/installation>`_
- Follow the ``pydanticAI`` `setup guide <https://ai.pydantic.dev/mcp/client/>`_
- Follow the ``mcp-use`` `setup guide <https://github.com/mcp-use/mcp-use>`_

External Access Considerations
----------------------------

While the APIs exposed through BioContextAI Core are free for academic research, they often are rate limited or ask users not to overburden their servers. When building AI systems, you should:

- Inform yourself on these limits
- Enact measures to reduce the reliance on these network calls when deploying to many users
- Consider caching of common tool calls, rate-limiting and optimizing your system prompt to use efficient tool calls
