import inspect
import sys
import functools
import asyncio
from typing import Any, Dict
from mcp.server.fastmcp import FastMCP
import act_core

# Initialize FastMCP server
mcp = FastMCP("ACT Compute Service")

def create_mcp_wrapper(func):
    """
    Creates a wrapper around an ACT function to normalize output
    to the {ok, data, meta} / {ok, error} format.
    """
    # We must preserve the signature for FastMCP inspection, 
    # but the return type will always be the normalized dict.
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Dict[str, Any]:
        try:
            # Call the synchronous act_core function
            # Note: FastMCP supports async, but act_core is sync.
            result = func(*args, **kwargs)
            
            return {
                "ok": True,
                "data": result,
                "meta": {}
            }
        except Exception as e:
            # Map exception types to error codes
            error_code = "INTERNAL_ERROR"
            if isinstance(e, ValueError):
                error_code = "INVALID_INPUT"
            elif isinstance(e, FileNotFoundError):
                error_code = "RESOURCE_NOT_FOUND" 
            elif isinstance(e, RuntimeError):
                error_code = "RUNTIME_ERROR"
                
            return {
                "ok": False,
                "error": {
                    "error_code": error_code,
                    "message": str(e),
                    "details": {}
                }
            }
    return wrapper

def register_act_tools():
    """
    Scans act_core module for public functions and registers them as MCP tools.
    """
    count = 0
    # Loop over all functions in act_core
    for name, func in inspect.getmembers(act_core, inspect.isfunction):
        # Skip private functions
        if name.startswith("_"):
            continue
            
        # Ensure it's defined in act_core (not an import)
        if func.__module__ != act_core.__name__:
            continue
            
        # Register the function
        # mcp.tool() is a decorator factory. We wrap the original function 
        # to ensure the MCP client sees the correct signature from the docstrings/annotations,
        # but the execution result is normalized.
        
        # Note: functools.wraps copies __annotations__. 
        # FastMCP uses these to build the schema.
        
        wrapped_func = create_mcp_wrapper(func)
        
        # We define a custom name to avoid potential conflicts, 
        # though function names like 'lookup_epa' are likely unique enough.
        # We rely on FastMCP's default naming (function name).
        
        mcp.tool()(wrapped_func)
        count += 1
        
    sys.stderr.write(f"Registered {count} tools from act_core.\n")

# Register tools immediately so they are available when importing 'mcp' for uvicorn
try:
    register_act_tools()
except Exception as e:
    sys.stderr.write(f"Critical error registering tools: {e}\n")
    # We don't exit here to avoid breaking imports if something minor fails,
    # but strictly speaking this is critical.
    pass

if __name__ == "__main__":
    try:
        # Run the server using stdio transport
        mcp.run()
    except Exception as e:
        sys.stderr.write(f"Critical error starting MCP server: {e}\n")
        sys.exit(1)
