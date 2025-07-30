#!/usr/bin/env python
# chuk_tool_processor/mcp/stream_manager.py
"""
StreamManager for CHUK Tool Processor.
"""
from __future__ import annotations

import asyncio
from typing import Any, Dict, List, Optional, Tuple

# --------------------------------------------------------------------------- #
#  CHUK imports                                                               #
# --------------------------------------------------------------------------- #
from chuk_mcp.config import load_config
from chuk_tool_processor.mcp.transport import (
    MCPBaseTransport,
    StdioTransport,
    SSETransport,
)
from chuk_tool_processor.logging import get_logger

logger = get_logger("chuk_tool_processor.mcp.stream_manager")


class StreamManager:
    """
    Manager for MCP server streams with support for multiple transport types.
    """

    # ------------------------------------------------------------------ #
    #  construction                                                      #
    # ------------------------------------------------------------------ #
    def __init__(self) -> None:
        self.transports: Dict[str, MCPBaseTransport] = {}
        self.server_info: List[Dict[str, Any]] = []
        self.tool_to_server_map: Dict[str, str] = {}
        self.server_names: Dict[int, str] = {}
        self.all_tools: List[Dict[str, Any]] = []
        self._lock = asyncio.Lock()
        self._close_tasks: List[asyncio.Task] = []  # Track cleanup tasks

    # ------------------------------------------------------------------ #
    #  factory helpers                                                   #
    # ------------------------------------------------------------------ #
    @classmethod
    async def create(
        cls,
        config_file: str,
        servers: List[str],
        server_names: Optional[Dict[int, str]] = None,
        transport_type: str = "stdio",
        default_timeout: float = 30.0,  # ADD: For consistency
    ) -> "StreamManager":
        inst = cls()
        await inst.initialize(
            config_file, 
            servers, 
            server_names, 
            transport_type,
            default_timeout=default_timeout  # PASS THROUGH
        )
        return inst

    @classmethod
    async def create_with_sse(
        cls,
        servers: List[Dict[str, str]],
        server_names: Optional[Dict[int, str]] = None,
        connection_timeout: float = 10.0,  # ADD: For SSE connection setup
        default_timeout: float = 30.0,     # ADD: For tool execution
    ) -> "StreamManager":
        inst = cls()
        await inst.initialize_with_sse(
            servers, 
            server_names,
            connection_timeout=connection_timeout,  # PASS THROUGH
            default_timeout=default_timeout         # PASS THROUGH
        )
        return inst

    # ------------------------------------------------------------------ #
    #  initialisation - stdio / sse                                      #
    # ------------------------------------------------------------------ #
    async def initialize(
        self,
        config_file: str,
        servers: List[str],
        server_names: Optional[Dict[int, str]] = None,
        transport_type: str = "stdio",
        default_timeout: float = 30.0,  # ADD: For consistency
    ) -> None:
        async with self._lock:
            self.server_names = server_names or {}

            for idx, server_name in enumerate(servers):
                try:
                    if transport_type == "stdio":
                        params = await load_config(config_file, server_name)
                        transport: MCPBaseTransport = StdioTransport(params)
                    elif transport_type == "sse":
                        # WARNING: For SSE transport, prefer using create_with_sse() instead
                        # This is a fallback for backward compatibility
                        logger.warning("Using SSE transport in initialize() - consider using initialize_with_sse() instead")
                        
                        # Try to extract URL from params or use localhost as fallback
                        if isinstance(params, dict) and 'url' in params:
                            sse_url = params['url']
                            api_key = params.get('api_key')
                        else:
                            sse_url = "http://localhost:8000"
                            api_key = None
                            logger.warning(f"No URL configured for SSE transport, using default: {sse_url}")
                        
                        transport = SSETransport(
                            sse_url,
                            api_key,
                            default_timeout=default_timeout
                        )
                    else:
                        logger.error("Unsupported transport type: %s", transport_type)
                        continue

                    if not await transport.initialize():
                        logger.error("Failed to init %s", server_name)
                        continue

                    #  store transport
                    self.transports[server_name] = transport

                    #  ping + gather tools
                    status = "Up" if await transport.send_ping() else "Down"
                    tools = await transport.get_tools()

                    for t in tools:
                        name = t.get("name")
                        if name:
                            self.tool_to_server_map[name] = server_name
                    self.all_tools.extend(tools)

                    self.server_info.append(
                        {
                            "id": idx,
                            "name": server_name,
                            "tools": len(tools),
                            "status": status,
                        }
                    )
                    logger.info("Initialised %s - %d tool(s)", server_name, len(tools))
                except Exception as exc:  # noqa: BLE001
                    logger.error("Error initialising %s: %s", server_name, exc)

            logger.info(
                "StreamManager ready - %d server(s), %d tool(s)",
                len(self.transports),
                len(self.all_tools),
            )

    async def initialize_with_sse(
        self,
        servers: List[Dict[str, str]],
        server_names: Optional[Dict[int, str]] = None,
        connection_timeout: float = 10.0,  # ADD: For SSE connection setup
        default_timeout: float = 30.0,     # ADD: For tool execution
    ) -> None:
        async with self._lock:
            self.server_names = server_names or {}

            for idx, cfg in enumerate(servers):
                name, url = cfg.get("name"), cfg.get("url")
                if not (name and url):
                    logger.error("Bad server config: %s", cfg)
                    continue
                try:
                    # FIXED: Pass timeout parameters to SSETransport
                    transport = SSETransport(
                        url, 
                        cfg.get("api_key"),
                        connection_timeout=connection_timeout,  # ADD THIS
                        default_timeout=default_timeout         # ADD THIS
                    )
                    
                    if not await transport.initialize():
                        logger.error("Failed to init SSE %s", name)
                        continue

                    self.transports[name] = transport
                    status = "Up" if await transport.send_ping() else "Down"
                    tools = await transport.get_tools()

                    for t in tools:
                        tname = t.get("name")
                        if tname:
                            self.tool_to_server_map[tname] = name
                    self.all_tools.extend(tools)

                    self.server_info.append(
                        {"id": idx, "name": name, "tools": len(tools), "status": status}
                    )
                    logger.info("Initialised SSE %s - %d tool(s)", name, len(tools))
                except Exception as exc:  # noqa: BLE001
                    logger.error("Error initialising SSE %s: %s", name, exc)

            logger.info(
                "StreamManager ready - %d SSE server(s), %d tool(s)",
                len(self.transports),
                len(self.all_tools),
            )

    # ------------------------------------------------------------------ #
    #  queries                                                           #
    # ------------------------------------------------------------------ #
    def get_all_tools(self) -> List[Dict[str, Any]]:
        return self.all_tools

    def get_server_for_tool(self, tool_name: str) -> Optional[str]:
        return self.tool_to_server_map.get(tool_name)

    def get_server_info(self) -> List[Dict[str, Any]]:
        return self.server_info
    
    async def list_tools(self, server_name: str) -> List[Dict[str, Any]]:
        """
        List all tools available from a specific server.
        
        This method is required by ProxyServerManager for proper tool discovery.
        
        Args:
            server_name: Name of the server to query
            
        Returns:
            List of tool definitions from the server
        """
        if server_name not in self.transports:
            logger.error(f"Server '{server_name}' not found in transports")
            return []
        
        # Get the transport for this server
        transport = self.transports[server_name]
        
        try:
            # Call the get_tools method on the transport
            tools = await transport.get_tools()
            logger.debug(f"Found {len(tools)} tools for server {server_name}")
            return tools
        except Exception as e:
            logger.error(f"Error listing tools for server {server_name}: {e}")
            return []

    # ------------------------------------------------------------------ #
    #  EXTRA HELPERS - ping / resources / prompts                        #
    # ------------------------------------------------------------------ #
    async def ping_servers(self) -> List[Dict[str, Any]]:
        async def _ping_one(name: str, tr: MCPBaseTransport):
            try:
                ok = await tr.send_ping()
            except Exception:  # pragma: no cover
                ok = False
            return {"server": name, "ok": ok}

        return await asyncio.gather(*(_ping_one(n, t) for n, t in self.transports.items()))

    async def list_resources(self) -> List[Dict[str, Any]]:
        out: List[Dict[str, Any]] = []

        async def _one(name: str, tr: MCPBaseTransport):
            if not hasattr(tr, "list_resources"):
                return
            try:
                res = await tr.list_resources()  # type: ignore[attr-defined]
                # accept either {"resources": [...]} **or** a plain list
                resources = (
                    res.get("resources", []) if isinstance(res, dict) else res
                )
                for item in resources:
                    item = dict(item)
                    item["server"] = name
                    out.append(item)
            except Exception as exc:
                logger.debug("resources/list failed for %s: %s", name, exc)

        await asyncio.gather(*(_one(n, t) for n, t in self.transports.items()))
        return out

    async def list_prompts(self) -> List[Dict[str, Any]]:
        out: List[Dict[str, Any]] = []

        async def _one(name: str, tr: MCPBaseTransport):
            if not hasattr(tr, "list_prompts"):
                return
            try:
                res = await tr.list_prompts()  # type: ignore[attr-defined]
                prompts = res.get("prompts", []) if isinstance(res, dict) else res
                for item in prompts:
                    item = dict(item)
                    item["server"] = name
                    out.append(item)
            except Exception as exc:
                logger.debug("prompts/list failed for %s: %s", name, exc)

        await asyncio.gather(*(_one(n, t) for n, t in self.transports.items()))
        return out

    # ------------------------------------------------------------------ #
    #  tool execution                                                    #
    # ------------------------------------------------------------------ #
    async def call_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        server_name: Optional[str] = None,
        timeout: Optional[float] = None,  # Timeout parameter already exists
    ) -> Dict[str, Any]:
        """
        Call a tool on the appropriate server with timeout support.
        
        Args:
            tool_name: Name of the tool to call
            arguments: Arguments to pass to the tool
            server_name: Optional server name (auto-detected if not provided)
            timeout: Optional timeout for the call
            
        Returns:
            Dictionary containing the tool result or error
        """
        server_name = server_name or self.get_server_for_tool(tool_name)
        if not server_name or server_name not in self.transports:
            # wording kept exactly for unit-test expectation
            return {
                "isError": True,
                "error": f"No server found for tool: {tool_name}",
            }
        
        transport = self.transports[server_name]
        
        # Apply timeout if specified
        if timeout is not None:
            logger.debug("Calling tool '%s' with %ss timeout", tool_name, timeout)
            try:
                # ENHANCED: Pass timeout to transport.call_tool if it supports it
                if hasattr(transport, 'call_tool'):
                    import inspect
                    sig = inspect.signature(transport.call_tool)
                    if 'timeout' in sig.parameters:
                        # Transport supports timeout parameter - pass it through
                        return await transport.call_tool(tool_name, arguments, timeout=timeout)
                    else:
                        # Transport doesn't support timeout - use asyncio.wait_for wrapper
                        return await asyncio.wait_for(
                            transport.call_tool(tool_name, arguments),
                            timeout=timeout
                        )
                else:
                    # Fallback to asyncio.wait_for
                    return await asyncio.wait_for(
                        transport.call_tool(tool_name, arguments),
                        timeout=timeout
                    )
            except asyncio.TimeoutError:
                logger.warning("Tool '%s' timed out after %ss", tool_name, timeout)
                return {
                    "isError": True,
                    "error": f"Tool call timed out after {timeout}s",
                }
        else:
            # No timeout specified, call directly
            return await transport.call_tool(tool_name, arguments)
        
    # ------------------------------------------------------------------ #
    #  shutdown - PROPERLY FIXED VERSION                                 #
    # ------------------------------------------------------------------ #
    async def close(self) -> None:
        """
        Properly close all transports with graceful handling of cancellation.
        """
        if not self.transports:
            return
        
        # Cancel any existing close tasks
        for task in self._close_tasks:
            if not task.done():
                task.cancel()
        self._close_tasks.clear()
        
        # Create close tasks for all transports
        close_tasks = []
        for name, transport in list(self.transports.items()):
            try:
                task = asyncio.create_task(
                    self._close_transport(name, transport), 
                    name=f"close_{name}"
                )
                close_tasks.append(task)
                self._close_tasks.append(task)
            except Exception as e:
                logger.debug(f"Error creating close task for {name}: {e}")
        
        # Wait for all close tasks with a timeout
        if close_tasks:
            try:
                # Give transports a reasonable time to close gracefully
                await asyncio.wait_for(
                    asyncio.gather(*close_tasks, return_exceptions=True),
                    timeout=2.0
                )
            except asyncio.TimeoutError:
                # Cancel any still-running tasks
                for task in close_tasks:
                    if not task.done():
                        task.cancel()
                # Brief wait for cancellation to take effect
                await asyncio.gather(*close_tasks, return_exceptions=True)
            except asyncio.CancelledError:
                # This is expected during event loop shutdown
                logger.debug("Close operation cancelled during shutdown")
            except Exception as e:
                logger.debug(f"Unexpected error during close: {e}")
        
        # Clean up state
        self._cleanup_state()
    
    async def _close_transport(self, name: str, transport: MCPBaseTransport) -> None:
        """Close a single transport with error handling."""
        try:
            await transport.close()
            logger.debug(f"Closed transport: {name}")
        except asyncio.CancelledError:
            # Re-raise cancellation
            raise
        except Exception as e:
            logger.debug(f"Error closing transport {name}: {e}")
    
    def _cleanup_state(self) -> None:
        """Clean up internal state (synchronous)."""
        self.transports.clear()
        self.server_info.clear()
        self.tool_to_server_map.clear()
        self.all_tools.clear()
        self._close_tasks.clear()

    # ------------------------------------------------------------------ #
    #  backwards-compat: streams helper                                  #
    # ------------------------------------------------------------------ #
    def get_streams(self) -> List[Tuple[Any, Any]]:
        """
        Return a list of ``(read_stream, write_stream)`` tuples for **all**
        transports.  Older CLI commands rely on this helper.
        """
        pairs: List[Tuple[Any, Any]] = []

        for tr in self.transports.values():
            if hasattr(tr, "get_streams") and callable(tr.get_streams):
                pairs.extend(tr.get_streams())  # type: ignore[arg-type]
                continue

            rd = getattr(tr, "read_stream", None)
            wr = getattr(tr, "write_stream", None)
            if rd and wr:
                pairs.append((rd, wr))

        return pairs

    # convenience alias
    @property
    def streams(self) -> List[Tuple[Any, Any]]:  # pragma: no cover
        return self.get_streams()