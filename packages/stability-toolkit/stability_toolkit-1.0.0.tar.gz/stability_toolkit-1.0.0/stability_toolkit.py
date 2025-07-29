# stability_toolkit.py

"""Core Stability Toolkit implementation."""

from typing import Any, List
import json
import os

# Environment variable support for API key
DEFAULT_API_KEY = os.getenv("STABILITY_API_KEY", "try-it-out")
API_URL_TEMPLATE = "https://rpc.stabilityprotocol.com/zkt/{}"
HEADERS = {"Content-Type": "application/json"}

__all__ = [
    "post_zkt_v1",
    "call_contract_read",
    "call_contract_write",
    "deploy_contract",
    "StabilityToolkit",
]

try:
    import requests
except ImportError:  # pragma: no cover
    requests = None  # type: ignore


def _sanitize_api_key_for_logging(api_key: str) -> str:
    """Sanitize API key for logging to prevent exposure."""
    if not api_key or api_key == "try-it-out":
        return api_key
    return f"{api_key[:8]}...{api_key[-4:]}" if len(api_key) > 12 else "***"


def _post_request(payload: dict, api_key: str = DEFAULT_API_KEY) -> str:
    """Send a POST request to the Stability API and return the response text."""
    if requests is None:
        raise RuntimeError("requests library is required")
    
    # Warn about try-it-out key limitations
    if api_key == "try-it-out":
        print("⚠️  Warning: Using 'try-it-out' API key (limited functionality)")
        print("   For production use, get a FREE API key at: https://portal.stabilityprotocol.com/")
        print("   Free tier: 1000 writes/month, 200 reads/minute, up to 3 keys")
    
    url = API_URL_TEMPLATE.format(api_key)
    try:
        response = requests.post(url, headers=HEADERS, json=payload)
        return response.text
    except Exception as e:  # pragma: no cover
        # Sanitize any potential API key exposure in error messages
        error_msg = str(e).replace(api_key, _sanitize_api_key_for_logging(api_key))
        return f"Error: {error_msg}"

try:
    from langchain_core.tools import BaseToolkit, tool
    _LANGCHAIN_AVAILABLE = True

    # ---- Tool 1: Write ZKTv1 message ----
    def post_zkt_v1(arguments: str, api_key: str = DEFAULT_API_KEY) -> str:
        """Send a simple string message to the blockchain."""
        payload = {"arguments": arguments}
        return _post_request(payload, api_key)

    # ---- Tool 2: Smart contract read ----
    def call_contract_read(
        to: str,
        abi: List[str],
        method: str,
        arguments: List[Any],
        id: int = 1,
        api_key: str = DEFAULT_API_KEY,
    ) -> str:
        """Execute a read-only smart contract call."""
        payload = {
            "to": to,
            "abi": abi,
            "method": method,
            "arguments": arguments,
            "id": id,
        }
        return _post_request(payload, api_key)

    # ---- Tool 3: Smart contract write ----
    def call_contract_write(
        to: str,
        abi: List[str],
        method: str,
        arguments: List[Any],
        wait: bool = True,
        id: int = 1,
        api_key: str = DEFAULT_API_KEY,
    ) -> str:
        """Execute a state-changing smart contract call."""
        payload = {
            "to": to,
            "abi": abi,
            "method": method,
            "arguments": arguments,
            "id": id,
            "wait": wait,
        }
        return _post_request(payload, api_key)

    # ---- Tool 4: Deploy contract ----
    def deploy_contract(
        code: str,
        arguments: List[Any] | None = None,
        wait: bool = False,
        id: int = 1,
        api_key: str = DEFAULT_API_KEY,
    ) -> str:
        """Deploy a Solidity contract to the blockchain."""
        payload = {
            "code": code,
            "arguments": arguments or [],
            "wait": wait,
            "id": id,
        }
        return _post_request(payload, api_key)

    # ---- LangChain tool wrappers using @tool decorator ----
    def create_stability_tools(api_key: str = DEFAULT_API_KEY):
        """Create Stability tools with specified API key."""
        
        @tool("StabilityWriteTool")
        def stability_write_tool(arguments: str) -> str:
            """Send a plain text message to the Stability blockchain using ZKT v1."""
            return post_zkt_v1(arguments, api_key)

        @tool("StabilityReadTool")
        def stability_read_tool(arguments: str) -> str:
            """Read data from a Stability smart contract using ZKT v2 read request. JSON input must include: to, abi, method, arguments."""
            return call_contract_read(**json.loads(arguments), api_key=api_key)

        @tool("StabilityWriteContractTool")
        def stability_write_contract_tool(arguments: str) -> str:
            """Write data to a Stability smart contract using ZKT v2 write request. JSON input must include: to, abi, method, arguments, id, wait."""
            return call_contract_write(**json.loads(arguments), api_key=api_key)

        @tool("StabilityDeployTool")
        def stability_deploy_tool(arguments: str) -> str:
            """Deploy a Solidity smart contract to the Stability blockchain. JSON input must include: code, arguments."""
            return deploy_contract(**json.loads(arguments), api_key=api_key)
        
        return [
            stability_write_tool,
            stability_read_tool,
            stability_write_contract_tool,
            stability_deploy_tool
        ]

    # ---- Toolkit class ----
    class StabilityToolkit(BaseToolkit):
        """Stability Blockchain Toolkit for LangChain.
        
        This toolkit provides AI agents with access to the Stability blockchain
        through Zero Gas Transaction (ZKT) API endpoints.
        
        Args:
            api_key: Stability API key. If not provided, will use STABILITY_API_KEY 
                    environment variable or default to "try-it-out"
        
        Environment Variables:
            STABILITY_API_KEY: Your Stability API key (recommended for production)
        
        Getting Your FREE API Key:
            Visit https://portal.stabilityprotocol.com/ to get your free API key.
            Free tier includes:
            - Up to 3 API keys per account
            - 1,000 write transactions per month  
            - 200 read operations per minute
            - Completely free access
        
        Support:
            Email: contact@stabilityprotocol.com
            Portal: https://portal.stabilityprotocol.com/
        
        Example:
            # Using environment variable (recommended)
            export STABILITY_API_KEY="your-api-key-from-portal"
            toolkit = StabilityToolkit()
            
            # Or passing directly
            toolkit = StabilityToolkit(api_key="your-api-key-from-portal")
            
            # Development/testing (limited functionality)
            toolkit = StabilityToolkit()  # Uses "try-it-out" key
        """
        
        api_key: str = DEFAULT_API_KEY
        
        def __init__(self, api_key: str | None = None, **kwargs):
            """Initialize the Stability toolkit.
            
            Args:
                api_key: Stability API key. If None, uses environment variable
                        STABILITY_API_KEY or defaults to "try-it-out"
            """
            # Set the api_key before calling super().__init__
            final_api_key = api_key or DEFAULT_API_KEY
            
            # Validate API key
            if not final_api_key:
                raise ValueError(
                    "API key is required. Get a FREE API key at https://portal.stabilityprotocol.com/ "
                    "or set STABILITY_API_KEY environment variable"
                )
            
            super().__init__(api_key=final_api_key, **kwargs)
            
            # Log API key status (sanitized)
            if self.api_key == "try-it-out":
                print("🔧 Stability Toolkit initialized with 'try-it-out' key (limited functionality)")
                print("   Get your FREE production API key at: https://portal.stabilityprotocol.com/")
            else:
                print(f"🔧 Stability Toolkit initialized with API key: {_sanitize_api_key_for_logging(self.api_key)}")
        
        def get_tools(self):
            """Get all Stability tools configured with this toolkit's API key."""
            return create_stability_tools(self.api_key)



except ImportError:  # pragma: no cover
    _LANGCHAIN_AVAILABLE = False
    
    class _BaseToolkitFallback:
        def get_tools(self):
            return []
    
    BaseToolkit = _BaseToolkitFallback  # type: ignore
    StabilityToolkit = _BaseToolkitFallback  # type: ignore
    
    def post_zkt_v1(*args, **kwargs):
        raise NotImplementedError("LangChain integration requires langchain-core")
    def call_contract_read(*args, **kwargs):
        raise NotImplementedError("LangChain integration requires langchain-core")
    def call_contract_write(*args, **kwargs):
        raise NotImplementedError("LangChain integration requires langchain-core")
    def deploy_contract(*args, **kwargs):
        raise NotImplementedError("LangChain integration requires langchain-core")
