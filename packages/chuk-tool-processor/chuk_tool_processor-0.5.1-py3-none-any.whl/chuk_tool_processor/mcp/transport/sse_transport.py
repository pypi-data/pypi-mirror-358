# chuk_tool_processor/mcp/transport/sse_transport.py
"""
Proper MCP SSE transport that follows the standard MCP SSE protocol.

This transport:
1. Connects to /sse for SSE stream
2. Listens for 'endpoint' event to get message URL  
3. Sends MCP initialize handshake FIRST
4. Only then proceeds with tools/list and tool calls
5. Handles async responses via SSE message events

FIXED: All hardcoded timeouts are now configurable parameters.
FIXED: Enhanced close method to avoid cancel scope conflicts.
"""
from __future__ import annotations

import asyncio
import contextlib
import json
import os
from typing import Any, Dict, List, Optional

import httpx

from .base_transport import MCPBaseTransport

# --------------------------------------------------------------------------- #
# Helpers                                                                     #
# --------------------------------------------------------------------------- #
DEFAULT_TIMEOUT = 30.0  # Default timeout for tool calls
DEFAULT_CONNECTION_TIMEOUT = 10.0  # Default timeout for connection setup
HEADERS_JSON: Dict[str, str] = {"accept": "application/json"}


def _url(base: str, path: str) -> str:
    """Join *base* and *path* with exactly one slash."""
    return f"{base.rstrip('/')}/{path.lstrip('/')}"


# --------------------------------------------------------------------------- #
# Transport                                                                   #
# --------------------------------------------------------------------------- #
class SSETransport(MCPBaseTransport):
    """
    Proper MCP SSE transport that follows the standard protocol:
    
    1. GET /sse → Establishes SSE connection
    2. Waits for 'endpoint' event → Gets message URL
    3. Sends MCP initialize handshake → Establishes session
    4. POST to message URL → Sends tool calls
    5. Waits for async responses via SSE message events
    """

    def __init__(
        self, 
        url: str, 
        api_key: Optional[str] = None,
        connection_timeout: float = DEFAULT_CONNECTION_TIMEOUT,
        default_timeout: float = DEFAULT_TIMEOUT
    ) -> None:
        """
        Initialize SSE Transport with configurable timeouts.
        
        Args:
            url: Base URL for the MCP server
            api_key: Optional API key for authentication
            connection_timeout: Timeout for connection setup (default: 10.0s)
            default_timeout: Default timeout for tool calls (default: 30.0s)
        """
        self.base_url = url.rstrip("/")
        self.api_key = api_key
        self.connection_timeout = connection_timeout
        self.default_timeout = default_timeout
        
        # NEW: Auto-detect bearer token from environment if not provided
        if not self.api_key:
            bearer_token = os.getenv("MCP_BEARER_TOKEN")
            if bearer_token:
                self.api_key = bearer_token
                print(f"🔑 Using bearer token from MCP_BEARER_TOKEN environment variable")

        # httpx client (None until initialise)
        self._client: httpx.AsyncClient | None = None
        self.session: httpx.AsyncClient | None = None

        # MCP SSE state
        self._message_url: Optional[str] = None
        self._session_id: Optional[str] = None
        self._sse_task: Optional[asyncio.Task] = None
        self._connected = asyncio.Event()
        self._initialized = asyncio.Event()  # NEW: Track MCP initialization
        
        # Async message handling
        self._pending_requests: Dict[str, asyncio.Future] = {}
        self._message_lock = asyncio.Lock()

    # ------------------------------------------------------------------ #
    # Life-cycle                                                         #
    # ------------------------------------------------------------------ #
    async def initialize(self) -> bool:
        """Initialize the MCP SSE transport."""
        if self._client:
            return True

        headers = {}
        if self.api_key:
            # NEW: Handle both "Bearer token" and just "token" formats
            if self.api_key.startswith("Bearer "):
                headers["Authorization"] = self.api_key
            else:
                headers["Authorization"] = f"Bearer {self.api_key}"
            print(f"🔑 Added Authorization header to httpx client")

        self._client = httpx.AsyncClient(
            headers=headers,
            timeout=self.default_timeout,  # Use configurable timeout
        )
        self.session = self._client

        # Start SSE connection and wait for endpoint
        self._sse_task = asyncio.create_task(self._handle_sse_connection())
        
        try:
            # FIXED: Use configurable connection timeout instead of hardcoded 10.0
            await asyncio.wait_for(self._connected.wait(), timeout=self.connection_timeout)
            
            # NEW: Send MCP initialize handshake
            if await self._initialize_mcp_session():
                return True
            else:
                print("❌ MCP initialization failed")
                return False
                
        except asyncio.TimeoutError:
            print("❌ Timeout waiting for SSE endpoint event")
            return False
        except Exception as e:
            print(f"❌ SSE initialization failed: {e}")
            return False

    async def _initialize_mcp_session(self) -> bool:
        """Send the required MCP initialize handshake."""
        if not self._message_url:
            print("❌ No message URL available for initialization")
            return False
        
        try:
            print("🔄 Sending MCP initialize handshake...")
            
            # Required MCP initialize message
            init_message = {
                "jsonrpc": "2.0",
                "id": "initialize",
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {},
                        "resources": {},
                        "prompts": {},
                        "sampling": {}
                    },
                    "clientInfo": {
                        "name": "chuk-tool-processor",
                        "version": "1.0.0"
                    }
                }
            }
            
            response = await self._send_message(init_message)
            
            if "result" in response:
                server_info = response["result"]
                print(f"✅ MCP initialized: {server_info.get('serverInfo', {}).get('name', 'Unknown Server')}")
                
                # Send initialized notification (required by MCP spec)
                notification = {
                    "jsonrpc": "2.0",
                    "method": "notifications/initialized"
                }
                
                # Send notification (don't wait for response)
                await self._send_notification(notification)
                self._initialized.set()
                return True
            else:
                print(f"❌ MCP initialization failed: {response}")
                return False
                
        except Exception as e:
            print(f"❌ MCP initialization error: {e}")
            return False

    async def _send_notification(self, notification: Dict[str, Any]) -> None:
        """Send a JSON-RPC notification (no response expected)."""
        if not self._client or not self._message_url:
            return
            
        try:
            headers = {"Content-Type": "application/json"}
            await self._client.post(
                self._message_url,
                json=notification,
                headers=headers
            )
        except Exception as e:
            print(f"⚠️ Failed to send notification: {e}")

    async def close(self) -> None:
        """Minimal close method with zero async operations."""
        # Just clear references - no async operations at all
        self._context_stack = None
        self.read_stream = None
        self.write_stream = None
    # ------------------------------------------------------------------ #
    # SSE Connection Handler                                             #
    # ------------------------------------------------------------------ #
    async def _handle_sse_connection(self) -> None:
        """Handle the SSE connection and extract the endpoint URL."""
        if not self._client:
            return

        try:
            headers = {
                "Accept": "text/event-stream",
                "Cache-Control": "no-cache"
            }
            
            async with self._client.stream(
                "GET", f"{self.base_url}/sse", headers=headers
            ) as response:
                response.raise_for_status()
                
                async for line in response.aiter_lines():
                    if not line:
                        continue
                        
                    # Parse SSE events
                    if line.startswith("event: "):
                        event_type = line[7:].strip()
                        
                    elif line.startswith("data: ") and 'event_type' in locals():
                        data = line[6:].strip()
                        
                        if event_type == "endpoint":
                            # Got the endpoint URL for messages - construct full URL
                            # NEW: Handle URLs that need trailing slash fix
                            if "/messages?" in data and "/messages/?" not in data:
                                data = data.replace("/messages?", "/messages/?", 1)
                                print(f"🔧 Fixed URL redirect: added trailing slash")
                            
                            self._message_url = f"{self.base_url}{data}"
                            
                            # Extract session_id if present
                            if "session_id=" in data:
                                self._session_id = data.split("session_id=")[1].split("&")[0]
                            
                            print(f"✅ Got message endpoint: {self._message_url}")
                            self._connected.set()
                            
                        elif event_type == "message":
                            # Handle incoming JSON-RPC responses
                            try:
                                message = json.loads(data)
                                await self._handle_incoming_message(message)
                            except json.JSONDecodeError:
                                print(f"❌ Failed to parse message: {data}")
                                
        except asyncio.CancelledError:
            pass
        except Exception as e:
            print(f"❌ SSE connection failed: {e}")

    async def _handle_incoming_message(self, message: Dict[str, Any]) -> None:
        """Handle incoming JSON-RPC response messages."""
        message_id = message.get("id")
        if message_id and message_id in self._pending_requests:
            # Complete the pending request
            future = self._pending_requests.pop(message_id)
            if not future.done():
                future.set_result(message)

    # ------------------------------------------------------------------ #
    # MCP Protocol Methods                                               #
    # ------------------------------------------------------------------ #
    async def send_ping(self) -> bool:
        """Test if we have a working and initialized connection."""
        return self._message_url is not None and self._initialized.is_set()

    async def get_tools(self) -> List[Dict[str, Any]]:
        """Get available tools using tools/list."""
        # NEW: Wait for initialization before proceeding
        if not self._initialized.is_set():
            print("⏳ Waiting for MCP initialization...")
            try:
                # FIXED: Use configurable connection timeout instead of hardcoded 10.0
                await asyncio.wait_for(self._initialized.wait(), timeout=self.connection_timeout)
            except asyncio.TimeoutError:
                print("❌ Timeout waiting for MCP initialization")
                return []
        
        if not self._message_url:
            return []
            
        try:
            message = {
                "jsonrpc": "2.0",
                "id": "tools_list",
                "method": "tools/list",
                "params": {}
            }
            
            response = await self._send_message(message)
            
            if "result" in response and "tools" in response["result"]:
                return response["result"]["tools"]
                
        except Exception as e:
            print(f"❌ Failed to get tools: {e}")
            
        return []

    async def call_tool(
        self, 
        tool_name: str, 
        arguments: Dict[str, Any],
        timeout: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Execute a tool call using the MCP protocol.
        
        Args:
            tool_name: Name of the tool to call
            arguments: Arguments to pass to the tool
            timeout: Optional timeout for this specific call
            
        Returns:
            Dictionary containing the tool result or error
        """
        # NEW: Ensure initialization before tool calls
        if not self._initialized.is_set():
            return {"isError": True, "error": "SSE transport not implemented"}
            
        if not self._message_url:
            return {"isError": True, "error": "No message endpoint available"}

        try:
            message = {
                "jsonrpc": "2.0",
                "id": f"call_{tool_name}",
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": arguments
                }
            }
            
            # Use provided timeout or fall back to default
            effective_timeout = timeout if timeout is not None else self.default_timeout
            response = await self._send_message(message, timeout=effective_timeout)
            
            # Process MCP response
            if "error" in response:
                return {
                    "isError": True,
                    "error": response["error"].get("message", "Unknown error")
                }
            
            if "result" in response:
                result = response["result"]
                
                # Handle MCP tool response format
                if "content" in result:
                    # Extract content from MCP format
                    content = result["content"]
                    if isinstance(content, list) and content:
                        # Take first content item
                        first_content = content[0]
                        if isinstance(first_content, dict) and "text" in first_content:
                            return {"isError": False, "content": first_content["text"]}
                    
                    return {"isError": False, "content": content}
                
                # Direct result
                return {"isError": False, "content": result}
            
            return {"isError": True, "error": "No result in response"}
            
        except Exception as e:
            return {"isError": True, "error": str(e)}

    async def _send_message(
        self, 
        message: Dict[str, Any],
        timeout: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Send a JSON-RPC message to the server and wait for async response.
        
        Args:
            message: JSON-RPC message to send
            timeout: Optional timeout for this specific message
            
        Returns:
            Response message from the server
        """
        if not self._client or not self._message_url:
            raise RuntimeError("Transport not properly initialized")

        message_id = message.get("id")
        if not message_id:
            raise ValueError("Message must have an ID")

        # Use provided timeout or fall back to default
        effective_timeout = timeout if timeout is not None else self.default_timeout

        # Create a future for this request
        future = asyncio.Future()
        async with self._message_lock:
            self._pending_requests[message_id] = future

        try:
            headers = {"Content-Type": "application/json"}
            
            # Send the request
            response = await self._client.post(
                self._message_url,
                json=message,
                headers=headers
            )
            
            # Check if server accepted the request
            if response.status_code == 202:
                # Server accepted - wait for async response via SSE
                try:
                    # FIXED: Use effective_timeout instead of hardcoded 30.0
                    response_message = await asyncio.wait_for(future, timeout=effective_timeout)
                    return response_message
                except asyncio.TimeoutError:
                    raise RuntimeError(f"Timeout waiting for response to message {message_id}")
            else:
                # Immediate response - parse and return
                response.raise_for_status()
                return response.json()
                
        finally:
            # Clean up pending request
            async with self._message_lock:
                self._pending_requests.pop(message_id, None)

    # ------------------------------------------------------------------ #
    # Additional MCP methods                                             #
    # ------------------------------------------------------------------ #
    async def list_resources(self) -> List[Dict[str, Any]]:
        """List available resources."""
        if not self._initialized.is_set() or not self._message_url:
            return []
            
        try:
            message = {
                "jsonrpc": "2.0",
                "id": "resources_list",
                "method": "resources/list",
                "params": {}
            }
            
            response = await self._send_message(message)
            if "result" in response and "resources" in response["result"]:
                return response["result"]["resources"]
                
        except Exception:
            pass
            
        return []

    async def list_prompts(self) -> List[Dict[str, Any]]:
        """List available prompts."""
        if not self._initialized.is_set() or not self._message_url:
            return []
            
        try:
            message = {
                "jsonrpc": "2.0",
                "id": "prompts_list", 
                "method": "prompts/list",
                "params": {}
            }
            
            response = await self._send_message(message)
            if "result" in response and "prompts" in response["result"]:
                return response["result"]["prompts"]
                
        except Exception:
            pass
            
        return []