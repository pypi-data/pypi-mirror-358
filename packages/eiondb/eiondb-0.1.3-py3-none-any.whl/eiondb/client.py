"""
Eion SDK Main Client

Main client class for interacting with Eion cluster management API.
"""

import os
import yaml
from typing import Optional, Dict, Any, List
from datetime import datetime
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .exceptions import (
    EionError,
    EionAuthenticationError,
    EionValidationError,
    EionNotFoundError,
    EionServerError,
    EionConnectionError,
    EionTimeoutError
)


class EionClient:
    """
    Main client for Eion cluster management operations.
    
    Provides cluster-level operations like user management, agent registration,
    session creation, and monitoring. This is for developers managing Eion clusters.
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        cluster_api_key: Optional[str] = None,
        config_file: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 3
    ):
        """
        Initialize the Eion client.

        Args:
            base_url: Base URL of the Eion server (e.g., "http://localhost:8080")
            cluster_api_key: API key for cluster authentication
            config_file: Path to YAML configuration file
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries for failed requests
        """
        # Load configuration from file if provided
        config = {}
        if config_file:
            try:
                with open(config_file, 'r') as f:
                    config = yaml.safe_load(f) or {}
            except FileNotFoundError:
                raise EionError(f"Configuration file not found: {config_file}")

        # Set configuration with precedence: args > env vars > config file > defaults
        self.base_url = (
            base_url or 
            os.getenv("EION_BASE_URL") or 
            config.get("base_url") or
            "http://localhost:8080"
        ).rstrip("/")

        self.cluster_api_key = (
            cluster_api_key or
            os.getenv("EION_CLUSTER_API_KEY") or
            config.get("cluster_api_key") or
            config.get("auth", {}).get("cluster_api_key")
        )

        # Set up requests session with retries
        self.session = requests.Session()
        
        retry_strategy = Retry(
            total=max_retries,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"],
            backoff_factor=1
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        self.timeout = timeout

    # ==========================================
    # HTTP CLIENT METHODS
    # ==========================================

    def _make_request(
        self,
        method: str,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Make an HTTP request to the Eion server"""
        
        # Prepare headers
        request_headers = {"Content-Type": "application/json"}
        if self.cluster_api_key:
            request_headers["Authorization"] = f"Bearer {self.cluster_api_key}"
        if headers:
            request_headers.update(headers)

        # Build URL
        url = f"{self.base_url}{endpoint}"

        try:
            response = self.session.request(
                method=method,
                url=url,
                json=json_data,
                params=params,
                headers=request_headers,
                timeout=self.timeout
            )

            # Handle different response status codes
            if response.status_code == 401:
                raise EionAuthenticationError("Authentication failed - check your cluster API key")
            elif response.status_code == 400:
                error_detail = response.json().get("error", "Bad request") if response.content else "Bad request"
                raise EionValidationError(f"Validation error: {error_detail}")
            elif response.status_code == 404:
                error_detail = response.json().get("error", "Resource not found") if response.content else "Resource not found"
                raise EionNotFoundError(f"Not found: {error_detail}")
            elif response.status_code >= 500:
                error_detail = response.json().get("error", "Server error") if response.content else "Server error"
                raise EionServerError(f"Server error: {error_detail}")
            elif not response.ok:
                error_detail = response.json().get("error", f"HTTP {response.status_code}") if response.content else f"HTTP {response.status_code}"
                raise EionError(f"Request failed: {error_detail}")

            # Return JSON response
            return response.json() if response.content else {}

        except requests.exceptions.Timeout:
            raise EionTimeoutError(f"Request timed out after {self.timeout} seconds")
        except requests.exceptions.ConnectionError:
            raise EionConnectionError(f"Failed to connect to Eion server at {self.base_url}")
        except requests.exceptions.RequestException as e:
            raise EionError(f"Request failed: {e}")

    # ==========================================
    # CLUSTER MANAGEMENT METHODS  
    # ==========================================

    def _get_headers(self) -> Dict[str, str]:
        """Get headers for cluster API requests."""
        return {
            "Authorization": f"Bearer {self.cluster_api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """Handle HTTP response and raise appropriate exceptions."""
        try:
            data = response.json() if response.content else {}
        except ValueError:
            data = {"error": "Invalid JSON response"}

        if response.status_code == 200:
            return data
        elif response.status_code == 201:
            return data
        elif response.status_code == 400:
            raise EionValidationError(
                data.get("error", "Validation error"), 
                status_code=response.status_code,
                response_data=data
            )
        elif response.status_code == 401:
            raise EionAuthenticationError(
                data.get("error", "Authentication failed"), 
                status_code=response.status_code,
                response_data=data
            )
        elif response.status_code == 403:
            raise EionAuthenticationError(
                data.get("error", "Access denied"), 
                status_code=response.status_code,
                response_data=data
            )
        elif response.status_code == 404:
            raise EionNotFoundError(
                data.get("error", "Resource not found"), 
                status_code=response.status_code,
                response_data=data
            )
        elif response.status_code == 409:
            raise EionValidationError(
                data.get("error", "Resource conflict"), 
                status_code=response.status_code,
                response_data=data
            )
        else:
            raise EionError(
                f"Unexpected status code: {response.status_code}",
                status_code=response.status_code,
                response_data=data
            )

    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request with error handling."""
        # Ensure endpoint ends with / to avoid redirects
        if not endpoint.endswith('/'):
            endpoint += '/'
        url = f"{self.base_url}/cluster/v1{endpoint}"
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                headers=self._get_headers(),
                timeout=self.timeout,
                **kwargs
            )
            return self._handle_response(response)
            
        except requests.exceptions.ConnectionError as e:
            raise EionConnectionError(f"Failed to connect to Eion server: {e}")
        except requests.exceptions.Timeout as e:
            raise EionTimeoutError(f"Request timed out: {e}")
        except requests.exceptions.RequestException as e:
            raise EionError(f"Request failed: {e}")

    # Health check
    def health_check(self) -> Dict[str, Any]:
        """Check Eion server health."""
        try:
            # Health endpoint doesn't require authentication
            response = requests.get(f"{self.base_url}/health", timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise EionConnectionError(f"Health check failed: {e}")

    def server_health(self) -> bool:
        """Check if Eion server is running and healthy."""
        try:
            health = self.health_check()
            return health.get("status") == "healthy"
        except Exception:
            return False

    # User Management
    def create_user(self, user_id: str, name: Optional[str] = None) -> Dict[str, Any]:
        """Create a new user."""
        data = {"user_id": user_id}
        if name:
            data["name"] = name
        return self._request("POST", "/users", json=data)

    def delete_user(self, user_id: str) -> Dict[str, Any]:
        """Delete a user."""
        return self._request("DELETE", f"/users/{user_id}")

    # Agent Management  
    def register_agent(
        self, 
        agent_id: str, 
        name: str, 
        permission: str = "r", 
        description: Optional[str] = None,
        guest: bool = False
    ) -> Dict[str, Any]:
        """Register a new agent."""
        data = {
            "agent_id": agent_id,
            "name": name,
            "permission": permission
        }
        if description:
            data["description"] = description
        if guest:
            data["guest"] = guest
        return self._request("POST", "/agents", json=data)

    def get_agent(self, agent_id: str) -> Dict[str, Any]:
        """Get agent details."""
        return self._request("GET", f"/agents/{agent_id}")

    def update_agent(self, agent_id: str, **updates) -> Dict[str, Any]:
        """Update agent properties."""
        data = {"agent_id": agent_id, **updates}
        return self._request("PUT", f"/agents/{agent_id}", json=data)

    def delete_agent(self, agent_id: str) -> Dict[str, Any]:
        """Delete an agent."""
        return self._request("DELETE", f"/agents/{agent_id}", json={"agent_id": agent_id})

    def list_agents(self, permission: Optional[str] = None, guest: Optional[bool] = None) -> List[Dict[str, Any]]:
        """List agents with optional filters."""
        params = {}
        if permission:
            params["permission"] = permission
        if guest is not None:
            params["guest"] = guest
        response = self._request("GET", "/agents", params=params)
        # Extract agents array from the response
        return response.get("agents", [])

    # Session Management
    def create_session(
        self,
        session_id: str,
        user_id: str,
        session_type_id: str = "default",
        session_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new session."""
        data = {
            "session_id": session_id,
            "user_id": user_id,
            "session_type_id": session_type_id
        }
        if session_name:
            data["session_name"] = session_name
        return self._request("POST", "/sessions", json=data)

    def delete_session(self, session_id: str) -> Dict[str, Any]:
        """Delete a session."""
        return self._request("DELETE", f"/sessions/{session_id}")

    # Agent Group Management
    def register_agent_group(
        self,
        agent_group_id: str,
        name: str,
        agent_ids: Optional[List[str]] = None,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """Register a new agent group."""
        data = {
            "agent_group_id": agent_group_id,
            "name": name
        }
        if agent_ids:
            data["agent_ids"] = agent_ids
        if description:
            data["description"] = description
        return self._request("POST", "/agent-groups", json=data)

    def list_agent_groups(self) -> List[Dict[str, Any]]:
        """List all agent groups."""
        return self._request("GET", "/agent-groups")

    def get_agent_group(self, group_id: str) -> Dict[str, Any]:
        """Get agent group details."""
        return self._request("GET", f"/agent-groups/{group_id}")

    def update_agent_group(self, group_id: str, **updates) -> Dict[str, Any]:
        """Update agent group properties."""
        data = {"agent_group_id": group_id, **updates}
        return self._request("PUT", f"/agent-groups/{group_id}", json=data)

    def delete_agent_group(self, group_id: str) -> Dict[str, Any]:
        """Delete an agent group."""
        return self._request("DELETE", f"/agent-groups/{group_id}", json={"agent_group_id": group_id})

    # Session Type Management
    def register_session_type(
        self,
        session_type_id: str,
        name: str,
        agent_group_ids: Optional[List[str]] = None,
        description: Optional[str] = None,
        encryption: str = "SHA256"
    ) -> Dict[str, Any]:
        """Register a new session type."""
        data = {
            "session_type_id": session_type_id,
            "name": name,
            "encryption": encryption
        }
        if agent_group_ids:
            data["agent_group_ids"] = agent_group_ids
        if description:
            data["description"] = description
        return self._request("POST", "/session-types", json=data)

    def list_session_types(self) -> List[Dict[str, Any]]:
        """List all session types."""
        return self._request("GET", "/session-types")

    def get_session_type(self, session_type_id: str) -> Dict[str, Any]:
        """Get session type details."""
        return self._request("GET", f"/session-types/{session_type_id}")

    def update_session_type(self, session_type_id: str, **updates) -> Dict[str, Any]:
        """Update session type properties."""
        data = {"session_type_id": session_type_id, **updates}
        return self._request("PUT", f"/session-types/{session_type_id}", json=data)

    def delete_session_type(self, session_type_id: str) -> Dict[str, Any]:
        """Delete a session type."""
        return self._request("DELETE", f"/session-types/{session_type_id}", json={"session_type_id": session_type_id})

    # Monitoring & Analytics
    def monitor_agent(self, agent_id: str, time_range: Dict[str, str]) -> Dict[str, Any]:
        """Get agent analytics for a time range."""
        params = {
            "start_time": time_range["start_time"],
            "end_time": time_range["end_time"]
        }
        return self._request("GET", f"/monitoring/agents/{agent_id}", params=params)

    def monitor_session(self, session_id: str) -> Dict[str, Any]:
        """Get session analytics."""
        return self._request("GET", f"/monitoring/sessions/{session_id}") 