"""MCP Server VSS Client package."""
from typing import Any, Dict, Optional, Union

import httpx
from loguru import logger

from mcp_server_vss.exceptions import VssError


class VssApiClient:
    """VSS API client with standardized error handling and multiple HTTP methods."""

    def __init__(self, auth_token: str, api_endpoint: str):
        """Initialize the VSS API client."""
        self.auth_token = auth_token
        self.api_endpoint = api_endpoint
        self._http_client: Optional[httpx.AsyncClient] = None
        self.user_agent = "mcp-server-vss/2025.6.1-dev4"

    async def __aenter__(self):
        """Enter the context manager."""
        self._http_client = httpx.AsyncClient(
            base_url=self.api_endpoint, timeout=30.0
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit the context manager."""
        if self._http_client:
            await self._http_client.aclose()

    async def _make_request(
        self,
        endpoint: str,
        context: str,
        method: str = "GET",
        data: Optional[Union[Dict[str, Any], str]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        content_type: Optional[str] = None,
    ) -> dict:
        """Make API request with standardized error handling.

        Args:
            endpoint: API endpoint path
            context: Context description for error messages
            method: HTTP method (GET, POST, PUT, DELETE, PATCH)
            data: Form data or raw data to send
            json_data: JSON data to send (takes precedence over data)
            params: Query parameters
            content_type: Override content type header
        """
        if not self._http_client:
            raise VssError("API client not initialized")

        # Prepare headers
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "User-Agent": f"{self.user_agent}",
        }

        # Set content type if provided
        if content_type:
            headers["Content-Type"] = content_type
        elif json_data is not None:
            headers["Content-Type"] = "application/json"

        # Prepare request kwargs
        request_kwargs = {"headers": headers, "params": params}

        # Add data based on type
        if json_data is not None:
            request_kwargs["json"] = json_data
        elif data is not None:
            if isinstance(data, str):
                request_kwargs["content"] = data
            else:
                request_kwargs["data"] = data

        try:
            # Make the request based on method
            method = method.upper()
            if method == "GET":
                response = await self._http_client.get(
                    endpoint, **request_kwargs
                )
            elif method == "POST":
                response = await self._http_client.post(
                    endpoint, **request_kwargs
                )
            elif method == "PUT":
                response = await self._http_client.put(
                    endpoint, **request_kwargs
                )
            elif method == "DELETE":
                response = await self._http_client.request(
                    method, url=endpoint, **request_kwargs
                )
            elif method == "PATCH":
                response = await self._http_client.patch(
                    endpoint, **request_kwargs
                )
            else:
                raise VssError(f"Unsupported HTTP method: {method}")

            return self._handle_response(response, context, method)

        except httpx.RequestError as e:
            logger.error(f"Request failed for {context} ({method}): {e}")
            raise VssError(f"Network error while {context}: {str(e)}")

    def _handle_response(
        self, response: httpx.Response, context: str, method: str = "GET"
    ) -> dict:
        """Standardize response handler with method-specific handling."""
        # Handle authentication errors
        if response.status_code == 401:
            raise VssError(
                "Unauthorized. Please check your MCP_VSS_AUTH_TOKEN."
            )

        # Handle not found errors
        if response.status_code == 404:
            raise VssError(f"Resource not found while {context}.")

        # Handle method-specific success codes
        if method in ["POST", "PUT", "PATCH"]:
            # These methods might return 201 (Created) or 202 (Accepted)
            if response.status_code in [200, 201, 202, 204]:
                return self._parse_response_body(response, context)
        elif method == "DELETE":
            # DELETE might return 204 (No Content) on success
            if response.status_code in [200, 202, 204]:
                # For 204, return empty dict or success message
                if response.status_code == 204:
                    return {
                        "message": "Resource deleted successfully",
                        "status": "success",
                    }
                return self._parse_response_body(response, context)
        else:  # GET and other methods
            if response.status_code == 200:
                return self._parse_response_body(response, context)

        # Handle other HTTP errors
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            logger.error(
                f"HTTP error {e.response.status_code} while {context} "
                f"({method})"
            )

            # Try to extract error details from response body
            error_detail = ""
            try:
                error_body = response.json()
                if isinstance(error_body, dict):
                    error_detail = error_body.get(
                        'message', error_body.get('error', '')
                    )
            except Exception:  # pylint: disable=broad-except
                # If the response body is not JSON, try to extract a
                # meaningful error message from the response text
                # (e.g. for 404 errors)
                error_detail = response.text[:200] if response.text else ""

            if error_detail:
                raise VssError(f"API error while {context}: {error_detail}")
            else:
                raise VssError(
                    f"API error while {context}: HTTP {e.response.status_code}"
                )

        # This shouldn't be reached, but just in case
        return self._parse_response_body(response, context)

    def _parse_response_body(
        self, response: httpx.Response, context: str
    ) -> dict:
        """Parse response body and handle API-level errors."""
        try:
            rv = response.json()
        except ValueError as e:
            logger.error(f"Invalid JSON response while {context}: {e}")
            raise VssError(f"Invalid response format while {context}")

        # Check for API-level errors in successful HTTP responses
        if isinstance(rv, dict) and 'message' in rv:
            error_msg = rv['message']
            if any(
                keyword in error_msg.lower()
                for keyword in ['error', 'failed', 'not found']
            ):
                raise VssError(f"API error: {error_msg}")

        return rv

    # Convenience methods for specific HTTP operations
    async def get(
        self,
        endpoint: str,
        context: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> dict:
        """Run convenience method for GET requests."""
        return await self._make_request(
            endpoint, context, "GET", params=params
        )

    async def post(
        self,
        endpoint: str,
        context: str,
        json_data: Optional[Dict[str, Any]] = None,
        data: Optional[Union[Dict[str, Any], str]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> dict:
        """Run convenience method for POST requests."""
        return await self._make_request(
            endpoint,
            context,
            "POST",
            data=data,
            json_data=json_data,
            params=params,
        )

    async def put(
        self,
        endpoint: str,
        context: str,
        json_data: Optional[Dict[str, Any]] = None,
        data: Optional[Union[Dict[str, Any], str]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> dict:
        """Run convenience method for PUT requests."""
        return await self._make_request(
            endpoint,
            context,
            "PUT",
            data=data,
            json_data=json_data,
            params=params,
        )

    async def patch(
        self,
        endpoint: str,
        context: str,
        json_data: Optional[Dict[str, Any]] = None,
        data: Optional[Union[Dict[str, Any], str]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> dict:
        """Run convenience method for PATCH requests."""
        return await self._make_request(
            endpoint,
            context,
            "PATCH",
            data=data,
            json_data=json_data,
            params=params,
        )

    async def delete(
        self,
        endpoint: str,
        context: str,
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> dict:
        """Run convenience method for DELETE requests."""
        return await self._make_request(
            endpoint, context, "DELETE", params=params, json_data=json_data
        )
