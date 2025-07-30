from typing import Dict, Any, List, Optional
from .api.payment_api import PaymentApi
from .api.client import ApiClient
from .errors import ApiError


class Charge:
    """High-level charge operations"""

    def __init__(self, api_client: Optional[ApiClient] = None):
        self.api = PaymentApi(api_client)

    def create_without_redirect(
        self,
        customer_id: str,
        price: int,
        description: Optional[str] = None,
        currency: str = "JPY",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a charge without redirect URLs

        Args:
            customer_id: Customer ID
            price: Charge amount
            description: Charge description
            currency: Currency code (default: JPY)
            **kwargs: Additional parameters

        Returns:
            Created charge data

        Raises:
            ApiError: If charge creation fails
        """
        try:
            # Create charge object
            charge = {"price": price, "currency": currency}

            if description:
                charge["description"] = description

            # Add any additional kwargs to charge object
            for key, value in kwargs.items():
                if key not in ["customer"]:
                    charge[key] = value

            # Build request body
            request_body = {"customer": customer_id, "charge": charge}

            return self.api.withdraw(request_body)
        except Exception as e:
            raise ApiError.from_error(e)

    def create_with_redirect(
        self,
        customer_id: str,
        price: int,
        success_url: str,
        failure_url: str,
        description: Optional[str] = None,
        currency: str = "JPY",
        expires_at: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a charge with redirect URLs for hosted checkout

        Args:
            customer_id: Customer ID
            price: Charge amount
            success_url: URL to redirect after successful payment
            failure_url: URL to redirect after failed payment
            description: Charge description
            currency: Currency code (default: JPY)
            expires_at: ISO-8601 format expiration date
            **kwargs: Additional parameters

        Returns:
            Created charge data with payment URL

        Raises:
            ApiError: If charge creation fails
        """
        try:
            # Create charge object
            charge = {"price": price, "currency": currency}

            if description:
                charge["description"] = description

            if expires_at:
                charge["expires_at"] = expires_at

            # Build request body
            request_body = {
                "customer": customer_id,
                "charge": charge,
                "redirect": {"success_url": success_url, "failure_url": failure_url},
            }

            # Add any remaining kwargs
            for key, value in kwargs.items():
                if key not in ["customer", "charge", "redirect"]:
                    request_body[key] = value

            return self.api.add_charge(request_body)
        except Exception as e:
            raise ApiError.from_error(e)

    def get(self, charge_id: str) -> Dict[str, Any]:
        """
        Get a specific charge

        Args:
            charge_id: Charge ID

        Returns:
            Charge data

        Raises:
            ApiError: If charge retrieval fails or charge not found
        """
        try:
            return self.api.get_charge(charge_id)
        except Exception as e:
            raise ApiError.from_error(e)

    def list(
        self,
        customer_id: str,
        page_size: Optional[int] = None,
        page_token: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        List charges for a customer

        Args:
            customer_id: Customer ID
            page_size: Number of charges per page
            page_token: Pagination token

        Returns:
            List of charges with pagination info

        Raises:
            ApiError: If charge listing fails
        """
        try:
            return self.api.get_charges(customer_id, page_size, page_token)
        except Exception as e:
            raise ApiError.from_error(e)

    def _get_auth_headers(self):
        """Debug method to check what authorization headers are being used"""
        if (
            hasattr(self.api, "api_client")
            and self.api.api_client
            and hasattr(self.api.api_client, "config")
        ):
            config = self.api.api_client.config
            if hasattr(config, "auth_settings") and "oauth2" in config.auth_settings:
                auth_setting = config.auth_settings["oauth2"]
                if callable(auth_setting.get("value")):
                    header_value = auth_setting["value"]()
                    return {auth_setting["key"]: header_value}
        return None
