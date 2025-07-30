from typing import Dict, Any, Optional, Tuple
from .client import ApiClient, Configuration


class CustomerApi:
    """Customer API operations"""

    def __init__(self, api_client: Optional[ApiClient] = None):
        self.api_client = api_client or ApiClient()

    def create(self, body: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Create a new customer"""
        data, status_code, headers = self.create_with_http_info(body, **kwargs)
        return data

    def create_with_http_info(
        self, body: Dict[str, Any], **kwargs
    ) -> Tuple[Any, int, Dict]:
        """Create customer with full HTTP info"""
        opts = {
            "body": body,
            "return_type": "object",
            "auth_names": ["oauth2"],
            "content_types": ["application/json"],
            "accepts": ["application/json"],
            **kwargs,
        }
        return self.api_client.call_api("POST", "/v1/customers", opts)

    def get(self, customer_id: str, **kwargs) -> Dict[str, Any]:
        """Get a specific customer"""
        data, status_code, headers = self.get_with_http_info(customer_id, **kwargs)
        return data

    def get_with_http_info(self, customer_id: str, **kwargs) -> Tuple[Any, int, Dict]:
        """Get customer with full HTTP info"""
        opts = {
            "return_type": "object",
            "auth_names": ["oauth2"],
            "accepts": ["application/json"],
            **kwargs,
        }
        return self.api_client.call_api("GET", f"/v1/customers/{customer_id}", opts)

    def update(
        self, customer_id: str, body: Dict[str, Any], **kwargs
    ) -> Dict[str, Any]:
        """Update a customer"""
        data, status_code, headers = self.update_with_http_info(
            customer_id, body, **kwargs
        )
        return data

    def update_with_http_info(
        self, customer_id: str, body: Dict[str, Any], **kwargs
    ) -> Tuple[Any, int, Dict]:
        """Update customer with full HTTP info"""
        opts = {
            "body": body,
            "return_type": "object",
            "auth_names": ["oauth2"],
            "content_types": ["application/json"],
            "accepts": ["application/json"],
            **kwargs,
        }
        return self.api_client.call_api("PUT", f"/v1/customers/{customer_id}", opts)

    def get_contract(self, customer_id: str, **kwargs) -> Dict[str, Any]:
        """Get contract for a customer"""
        data, status_code, headers = self.get_contract_with_http_info(
            customer_id, **kwargs
        )
        return data

    def get_contract_with_http_info(
        self, customer_id: str, **kwargs
    ) -> Tuple[Any, int, Dict]:
        """Get customer contract with full HTTP info"""
        opts = {
            "return_type": "object",
            "auth_names": ["oauth2"],
            "accepts": ["application/json"],
            **kwargs,
        }
        return self.api_client.call_api(
            "GET", f"/v1/customers/{customer_id}/contract", opts
        )

    def delete(self, customer_id: str, **kwargs) -> Dict[str, Any]:
        """Delete a customer"""
        data, status_code, headers = self.delete_with_http_info(customer_id, **kwargs)
        return data

    def delete_with_http_info(
        self, customer_id: str, **kwargs
    ) -> Tuple[Any, int, Dict]:
        """Delete customer with full HTTP info"""
        opts = {
            "return_type": "object",
            "auth_names": ["oauth2"],
            "accepts": ["application/json"],
            **kwargs,
        }
        return self.api_client.call_api("DELETE", f"/v1/customers/{customer_id}", opts)
