from typing import Dict, Any, Optional
from .api.payment_api import PaymentApi
from .api.client import ApiClient
from .errors import ApiError


class Payment:
    """High-level payment operations"""

    def __init__(self, api_client: Optional[ApiClient] = None):
        self.api = PaymentApi(api_client)

    def on_session(
        self,
        customer_id: Optional[str] = None,
        price: Optional[int] = None,
        description: Optional[str] = None,
        expires_at: Optional[str] = None,
        redirect_urls: Optional[Dict[str, str]] = None,
        buyer: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Process an on-session payment (customer present)

        Args:
            customer_id: Customer ID (optional)
            price: Payment amount (optional)
            description: Description of the charge
            expires_at: ISO-8601 format expiration date (e.g. "2025-06-01T00:00:00Z")
            redirect_urls: Dict containing success_url and failure_url
            buyer: Customer information (email, phone, name, etc.)
            **kwargs: Additional parameters

        Returns:
            Payment result

        Raises:
            ApiError: If payment processing fails
        """
        try:
            # Build the base request
            request_body = {}

            # Add customer ID if provided
            if customer_id is not None:
                request_body["customer"] = customer_id

            # Create charge object only if price is provided
            if price is not None:
                charge = {"price": price}
                if description:
                    charge["description"] = description

                # Add expires_at to charge object if provided
                if expires_at:
                    charge["expires_at"] = expires_at

                request_body["charge"] = charge

            # Handle buyer information
            buyer_dict = buyer or {}  # Use provided buyer or create empty dict

            # If no charge object (no price) and expires_at is provided, add expires_at to buyer
            if price is None and expires_at is not None:
                buyer_dict["expires_at"] = expires_at

            # Add buyer to request if it's not empty
            if buyer_dict:
                request_body["buyer"] = buyer_dict

            # Add redirect URLs if provided
            if redirect_urls:
                request_body["redirect"] = redirect_urls

            # Add any additional parameters
            for key, value in kwargs.items():
                if key not in request_body:
                    request_body[key] = value

            return self.api.on_session_payment(request_body)
        except Exception as e:
            raise ApiError.from_error(e)

    def off_session(
        self,
        customer_id: str,
        price: int,
        description: Optional[str] = None,
        expires_at: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Process an off-session payment (customer not present)

        Args:
            customer_id: Customer ID
            price: Charge amount
            description: Description of the charge
            expires_at: ISO-8601 format expiration date (e.g. "2025-06-01T00:00:00Z")
            **kwargs: Additional parameters for the charge object

        Returns:
            Payment result

        Raises:
            ApiError: If payment processing fails
        """
        try:
            # Create charge object
            charge = {"price": price}

            # Add optional parameters to charge object
            if description:
                charge["description"] = description

            if expires_at:
                charge["expires_at"] = expires_at

            # Add any additional kwargs to the charge object
            for key, value in kwargs.items():
                if key not in ["customer"]:  # Exclude parameters that go at the top level
                    charge[key] = value

            # Build the complete request body
            request_body = {"customer": customer_id, "charge": charge}

            return self.api.off_session_payment(request_body)
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
