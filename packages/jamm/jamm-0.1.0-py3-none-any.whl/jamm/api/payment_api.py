from typing import Dict, Any, Optional, Tuple
from .client import ApiClient


class PaymentApi:
    """Payment API operations"""

    def __init__(self, api_client: Optional[ApiClient] = None):
        self.api_client = api_client or ApiClient()

    def create_contract_with_charge(
        self, body: Dict[str, Any], **kwargs
    ) -> Dict[str, Any]:
        """Create a contract with initial charge"""
        data, status_code, headers = self.create_contract_with_charge_with_http_info(
            body, **kwargs
        )
        return data

    def create_contract_with_charge_with_http_info(
        self, body: Dict[str, Any], **kwargs
    ) -> Tuple[Any, int, Dict]:
        """Create contract with charge and full HTTP info"""
        opts = {
            "body": body,
            "return_type": "object",
            "auth_names": ["oauth2"],
            "content_types": ["application/json"],
            "accepts": ["application/json"],
            **kwargs,
        }
        return self.api_client.call_api("POST", "/v1/contract-with-charge", opts)

    def create_contract_without_charge(
        self, body: Dict[str, Any], **kwargs
    ) -> Dict[str, Any]:
        """Create a contract without initial charge"""
        data, status_code, headers = self.create_contract_without_charge_with_http_info(
            body, **kwargs
        )
        return data

    def create_contract_without_charge_with_http_info(
        self, body: Dict[str, Any], **kwargs
    ) -> Tuple[Any, int, Dict]:
        """Create contract without charge and full HTTP info"""
        opts = {
            "body": body,
            "return_type": "object",
            "auth_names": ["oauth2"],
            "content_types": ["application/json"],
            "accepts": ["application/json"],
            **kwargs,
        }
        return self.api_client.call_api("POST", "/v1/contract-without-charge", opts)

    def add_charge(self, body: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Add charge to existing contract"""
        data, status_code, headers = self.add_charge_with_http_info(body, **kwargs)
        return data

    def add_charge_with_http_info(
        self, body: Dict[str, Any], **kwargs
    ) -> Tuple[Any, int, Dict]:
        """Add charge with full HTTP info"""
        opts = {
            "body": body,
            "return_type": "object",
            "auth_names": ["oauth2"],
            "content_types": ["application/json"],
            "accepts": ["application/json"],
            **kwargs,
        }

        return self.api_client.call_api("POST", "/v1/add-charge", opts)

    def get_charge(self, charge_id: str, **kwargs) -> Dict[str, Any]:
        """Get a specific charge"""
        data, status_code, headers = self.get_charge_with_http_info(charge_id, **kwargs)
        return data

    def get_charge_with_http_info(
        self, charge_id: str, **kwargs
    ) -> Tuple[Any, int, Dict]:
        """Get charge with full HTTP info"""
        opts = {
            "return_type": "object",
            "auth_names": ["oauth2"],
            "accepts": ["application/json"],
            **kwargs,
        }
        return self.api_client.call_api("GET", f"/v1/charge/{charge_id}", opts)

    def get_charges(
        self,
        customer_id: str,
        pagination_page_size: Optional[int] = None,
        pagination_page_token: Optional[str] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """Get list of charges for a customer"""
        data, status_code, headers = self.get_charges_with_http_info(
            customer_id, pagination_page_size, pagination_page_token, **kwargs
        )
        return data

    def get_charges_with_http_info(
        self,
        customer_id: str,
        pagination_page_size: Optional[int] = None,
        pagination_page_token: Optional[str] = None,
        **kwargs,
    ) -> Tuple[Any, int, Dict]:
        """Get charges with full HTTP info"""
        query_params = {}
        if pagination_page_size is not None:
            query_params["pagination.pageSize"] = pagination_page_size
        if pagination_page_token is not None:
            query_params["pagination.pageToken"] = pagination_page_token

        opts = {
            "query_params": query_params if query_params else None,
            "return_type": "object",
            "auth_names": ["oauth2"],
            "accepts": ["application/json"],
            **kwargs,
        }
        return self.api_client.call_api("GET", f"/v1/charges/{customer_id}", opts)

    def on_session_payment(self, body: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Process on-session payment"""
        data, status_code, headers = self.on_session_payment_with_http_info(
            body, **kwargs
        )
        return data

    def on_session_payment_with_http_info(
        self, body: Dict[str, Any], **kwargs
    ) -> Tuple[Any, int, Dict]:
        """On-session payment with full HTTP info"""
        opts = {
            "body": body,
            "return_type": "object",
            "auth_names": ["oauth2"],
            "content_types": ["application/json"],
            "accepts": ["application/json"],
            **kwargs,
        }
        return self.api_client.call_api("POST", "/v1/payments/on-session", opts)

    def off_session_payment(self, body: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Process off-session payment"""
        data, status_code, headers = self.off_session_payment_with_http_info(
            body, **kwargs
        )
        return data

    def off_session_payment_with_http_info(
        self, body: Dict[str, Any], **kwargs
    ) -> Tuple[Any, int, Dict]:
        """Off-session payment with full HTTP info"""
        opts = {
            "body": body,
            "return_type": "object",
            "auth_names": ["oauth2"],
            "content_types": ["application/json"],
            "accepts": ["application/json"],
            **kwargs,
        }
        return self.api_client.call_api("POST", "/v1/payments/off-session", opts)

    def withdraw(self, body: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Process a withdrawal"""
        data, status_code, headers = self.withdraw_with_http_info(body, **kwargs)
        return data

    def withdraw_with_http_info(
        self, body: Dict[str, Any], **kwargs
    ) -> Tuple[Any, int, Dict]:
        """Withdraw with full HTTP info"""
        opts = {
            "body": body,
            "return_type": "object",
            "auth_names": ["oauth2"],
            "content_types": ["application/json"],
            "accepts": ["application/json"],
            **kwargs,
        }
        return self.api_client.call_api("POST", "/v1/withdraw", opts)
