from typing import Dict, Any, Optional
from .api.payment_api import PaymentApi
from .api.customer_api import CustomerApi
from .api.client import ApiClient
from .errors import ApiError


class Contract:
    """High-level contract operations"""

    def __init__(self, api_client: Optional[ApiClient] = None):
        self.payment_api = PaymentApi(api_client)
        self.customer_api = CustomerApi(api_client)

    def create_with_charge(
        self,
        buyer: Dict[str, Any],
        charge: Dict[str, Any],
        redirect: Dict[str, Any],
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a contract with initial charge

        Args:
            buyer: Buyer information
            charge: Initial charge details
            redirect: Redirect URLs
            **kwargs: Additional parameters

        Returns:
            Contract creation response with payment link

        Raises:
            ApiError: If contract creation fails
        """
        try:
            request_body = {
                "buyer": buyer,
                "charge": charge,
                "redirect": redirect,
                **kwargs,
            }
            return self.payment_api.create_contract_with_charge(request_body)
        except Exception as e:
            raise ApiError.from_error(e)

    def create_without_charge(
        self, buyer: Dict[str, Any], redirect: Dict[str, Any], **kwargs
    ) -> Dict[str, Any]:
        """
        Create a contract without initial charge

        Args:
            buyer: Buyer information
            redirect: Redirect URLs
            **kwargs: Additional parameters

        Returns:
            Contract creation response

        Raises:
            ApiError: If contract creation fails
        """
        try:
            request_body = {"buyer": buyer, "redirect": redirect, **kwargs}
            return self.payment_api.create_contract_without_charge(request_body)
        except Exception as e:
            raise ApiError.from_error(e)

    def get(self, customer_id: str) -> Optional[Dict[str, Any]]:
        """
        Get contract for a customer

        Args:
            customer_id: Customer ID

        Returns:
            Contract data or None if not found
        """
        try:
            return self.customer_api.get_contract(customer_id)
        except Exception as e:
            if hasattr(e, "status") and e.status == 404:
                return None
            elif hasattr(e, "code") and e.code == 404:
                return None
            elif "404" in str(e) or "not found" in str(e).lower():
                return None
            else:
                raise ApiError.from_error(e)

    def _get_auth_headers(self):
        """Debug method to check what authorization headers are being used"""
        if (
            hasattr(self.payment_api, "api_client")
            and self.payment_api.api_client
            and hasattr(self.payment_api.api_client, "config")
        ):
            config = self.payment_api.api_client.config
            if hasattr(config, "auth_settings") and "oauth2" in config.auth_settings:
                auth_setting = config.auth_settings["oauth2"]
                if callable(auth_setting.get("value")):
                    header_value = auth_setting["value"]()
                    return {auth_setting["key"]: header_value}
        return None
