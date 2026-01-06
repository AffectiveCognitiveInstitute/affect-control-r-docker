#!/bin/bash
set -e

# Default to REST if not set
MODE=${RUN_MODE:-REST}

if [ "$MODE" = "MCP" ]; then
    echo "Starting MCP Server (SSE transport)..."
    exec python3 mcp_server.py
else
    echo "Starting REST API (Gunicorn)..."
    exec gunicorn --bind 0.0.0.0:5000 --timeout 120 --log-level debug app:app
fi
