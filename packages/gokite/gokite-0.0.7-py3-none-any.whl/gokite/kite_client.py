import os
import requests
import json
from typing import Optional, Dict, Any
from .exceptions import KiteError, KiteAuthenticationError, KiteNetworkError, KiteNotFoundError
from .util import (
    openapi_to_description,
    find_matching_endpoint,
    extract_input_fields_from_schema,
    extract_response_fields_from_schema,
    validate_payload_against_openapi
)

class KiteClient:
    """
    Kite SDK Client for interacting with Kite backend and blockchain layer.
    """

    DEFAULT_API_BASE_URL = "https://neo.staging.gokite.ai"  # Example base URL, replace with actual if different

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None
    ):
        self.api_key = api_key or os.environ.get("KITE_API_KEY")
        if not self.api_key:
            raise KiteAuthenticationError("Missing KITE_API_KEY")

        self.base_url = base_url or self.DEFAULT_API_BASE_URL
        self.session = requests.Session()
        self.session.headers.update({
            "X-API-KEY": f"{self.api_key}",
            "Content-Type": "application/json"
        })
        # cache service details
        self._service_details = {}

    def make_payment(self, to_address: str, amount: float) -> str:
        """Make on-chain payment"""
        raise NotImplementedError("MakePayment is not implemented yet")

    def _get_service_details(self, service_id: str) -> Dict[str, Any]:
        """
        Fetch service details from /v1/asset endpoint with caching.

        Args:
            service_id: The service ID to fetch details for

        Returns:
            Dictionary containing service details including service_url and schema
        """
        # try load from cache
        if service_id in self._service_details:
            return self._service_details[service_id]

        url = f"{self.base_url}/v1/asset?"
        if service_id.startswith("agent_"):
            url += f"id={service_id}"
        else:
            url += f"name={service_id}"

        try:
            response = self.session.get(url)
        except Exception as e:
            raise KiteNetworkError(e)

        result = self._handle_response(response)
        if not result.get("data"):
            raise KiteError(f"Invalid response (status {response.status_code}): {result.get('error', response.text)}")

        # Cache service response
        self._service_details[result["data"]["id"]] = result["data"]
        return result["data"]

    def load_service_description(self, service_id: str) -> str:
        """Load service description from cached service details"""
        service_details = self._get_service_details(service_id)
        return service_details.get("description")

    def load_service_input_fields(self, service_id: str) -> Dict[str, str]:
        """
        Load service input fields from OpenAPI schema.

        Args:
            service_id: The service ID to get input fields for

        Returns:
            Dictionary mapping parameter names to their data types.
            For GET methods, returns empty dict.
            For POST/PUT/PATCH methods, returns dict of request body parameters.
        """
        service_details = self._get_service_details(service_id)
        schema = service_details.get("schema")
        service_url = service_details.get("service_url")

        if not schema or not service_url:
            return {}

        try:
            schema_json = json.loads(schema)
            return extract_input_fields_from_schema(schema_json, service_url)
        except Exception as e:
            print(f"Warning: Error extracting input fields from schema: {e}")
            return {}

    def load_service_response_fields(self, service_id: str) -> Dict[str, str]:
        """
        Load service response fields from OpenAPI schema.

        Args:
            service_id: The service ID to get response fields for

        Returns:
            Dictionary mapping parameter names to their data types.
        """
        service_details = self._get_service_details(service_id)
        schema = service_details.get("schema")
        service_url = service_details.get("service_url")

        if not schema or not service_url:
            return {}

        try:
            schema_json = json.loads(schema)
            return extract_response_fields_from_schema(schema_json, service_url)
        except Exception as e:
            print(f"Warning: Error extracting response fields from schema: {e}")
            return {}

    def call_service(self, service_id: str, payload: dict, headers: dict = {}) -> dict:
        """
        Call a service with payload validation against OpenAPI schema.

        Args:
            service_id: The service ID to call
            payload: The payload to send to the service
            headers: Additional headers to include in the request

        Returns:
            Response from the service
        """
        # Get service details including service_url and schema
        try:
            service_details = self._get_service_details(service_id)
        except Exception as e:
            raise KiteError(f"Failed to get service details for service {service_id}: {e}")

        service_url = service_details.get("service_url")
        if not service_url:
            raise KiteError(f"No service_url found for service {service_id}")

        schema = service_details.get("schema")
        http_method = "post"  # Default method

        if schema:
            try:
                schema_json = json.loads(schema)
                # Find matching endpoint and method
                path, method = find_matching_endpoint(service_url, schema_json)
                if path and method:
                    http_method = method
                    # Validate payload against OpenAPI schema for the specific endpoint
                    validate_payload_against_openapi(payload, schema_json, path, method)
                else:
                    print(f"Warning: No matching endpoint found in schema for service URL: {service_url}")
            except Exception as e:
                print(f"Warning: Error processing OpenAPI schema: {e}")

        try:
            # Make request with the determined HTTP method
            if http_method.lower() == "get":
                # For GET requests, send payload as query parameters
                response = requests.get(service_url, params=payload, headers=headers)
            elif http_method.lower() == "post":
                response = requests.post(service_url, json=payload, headers=headers)
            elif http_method.lower() == "put":
                response = requests.put(service_url, json=payload, headers=headers)
            elif http_method.lower() == "patch":
                response = requests.patch(service_url, json=payload, headers=headers)
            else:
                # Fallback to POST for unknown methods
                response = requests.post(service_url, json=payload, headers=headers)

        except Exception as e:
            raise KiteNetworkError(f"Failed to call service {service_id}: {e}")

        result = self._handle_service_response(response)

        # Submit receipt
        volume = self._calculate_volume(service_id, payload)
        success = self._submit_receipt(service_id, volume)
        if not success:
            print(f"Warning: failed to submit receipt for service {service_id}")

        return result

    def _calculate_volume(self, service_id: str, payload: dict) -> int:
        """
        Calculate the volume of the payload.
        """
        # TODO: implement volume calculation
        return 1

    def _submit_receipt(self, service_id: str, total_volume: int):
        url = f"{self.base_url}/v3/submit_receipt"
        try:
            response = self.session.post(url, json={
                "service_id": service_id,
                "total_volume": total_volume
            })
        except Exception as e:
            raise KiteNetworkError(e)
        try:
            self._handle_response(response)
            return True
        except Exception:
            return False

    def get_service_info(self, service_id: str) -> str:
        """
        Get a human-readable description of the service including endpoints and request/response format.

        Args:
            service_id: The service ID to get information for

        Returns:
            Human-readable description of the service
        """
        try:
            service_details = self._get_service_details(service_id)
        except Exception as e:
            raise KiteError(f"Failed to get service details for service {service_id}: {e}")

        schema = service_details.get("schema")
        description = service_details.get("description", "No description available")

        # Build the human-readable description
        info_parts = []

        # Basic service info
        info_parts.append(f"Service ID: {service_id}")
        info_parts.append(f"Description: {description}")

        if schema:
            try:
                schema_json = json.loads(schema)
                info_parts.append(openapi_to_description(schema_json))
            except Exception as e:
                info_parts.append(f"Error parsing OpenAPI schema: {e}")
        else:
            info_parts.append("\nNo OpenAPI schema available for this service")

        return "\n".join(info_parts)

    def _handle_response(self, response):
        """Handle HTTP response uniformly"""
        try:
            data = response.json()
        except requests.exceptions.JSONDecodeError:
            raise KiteError("Invalid response from server")

        if 200 <= response.status_code < 300:
            return data

        if response.status_code == 401 or response.status_code == 403:
            raise KiteAuthenticationError(
                f"Authentication failed (status {response.status_code}): {data.get('error', response.text)}"
            )
        elif response.status_code == 404:
            raise KiteNotFoundError(
                f"Resource not found (status {response.status_code}): {data.get('error', response.text)}"
            )
        elif 400 <= response.status_code < 500:
            raise KiteError(
                f"Client error (status {response.status_code}): {data.get('error', response.text)}"
            )
        elif 500 <= response.status_code < 600:
            raise KiteError(
                f"Server error (status {response.status_code}): {data.get('error', response.text)}"
            )
        else:
            error_msg = data.get("error", "Unknown error")
            raise KiteError(error_msg)

    def _handle_service_response(self, response: requests.Response) -> dict:
        """Handle service response uniformly"""
        try:
            data = response.json()
        except requests.exceptions.JSONDecodeError:
            raise KiteError("Invalid response from server")

        if 200 <= response.status_code < 300:
            return data

        raise KiteError(f"Service error (status {response.status_code}): {data.get('error', response.text)}")
