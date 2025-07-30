from typing import Dict, Any, Optional
from .api.customer_api import CustomerApi
from .api.client import ApiClient
from .errors import ApiError


class Customer:
    """High-level customer operations"""

    def __init__(self, api_client: Optional[ApiClient] = None):
        self.api = CustomerApi(api_client)

    @property
    def KycStatus(self):
        """Access to KYC status enums"""
        try:
            from .models import KycStatus

            return KycStatus
        except ImportError:

            class MockKycStatus:
                APPROVED = "APPROVED"
                DENIED = "DENIED"
                IN_REVIEW = "IN_REVIEW"
                NOT_SUBMITTED = "NOT_SUBMITTED"

            return MockKycStatus

    @property
    def PaymentAuthorizationStatus(self):
        """Access to payment authorization status enums"""
        try:
            from .models import PaymentAuthorizationStatus

            return PaymentAuthorizationStatus
        except ImportError:

            class MockPaymentAuthorizationStatus:
                AUTHORIZED = "AUTHORIZED"
                NOT_AUTHORIZED = "NOT_AUTHORIZED"

            return MockPaymentAuthorizationStatus

    def create(self, buyer: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a customer

        Args:
            buyer: Customer data

        Returns:
            Customer object

        Raises:
            ApiError: If API call fails
        """
        try:
            request_body = {"buyer": buyer}
            r = self.api.create(request_body)

            if isinstance(r, dict) and "customer" in r:
                return r["customer"]
            else:
                return r
        except Exception as e:
            raise ApiError.from_error(e)

    def get(self, id_or_email: str) -> Dict[str, Any]:
        """
        Get a customer by ID or email

        Args:
            id_or_email: Customer ID or email

        Returns:
            Customer object with activated flag properly set

        Raises:
            ApiError: If customer not found or API error occurs
        """
        try:
            r = self.api.get(id_or_email)

            if isinstance(r, dict) and "customer" in r:
                customer = r["customer"]
            else:
                customer = r

            if customer.get("activated") is None:
                customer["activated"] = False

            return customer
        except Exception as e:
            raise ApiError.from_error(e)

    def get_contract(self, customer_id: str) -> Optional[Dict[str, Any]]:
        """
        Get customer contract

        Args:
            customer_id: Customer ID

        Returns:
            Contract data or None if not found
        """
        try:
            return self.api.get_contract(customer_id)
        except Exception as e:
            if hasattr(e, "status") and e.status == 404:
                return None
            elif hasattr(e, "code") and e.code == 404:
                return None
            elif "404" in str(e) or "not found" in str(e).lower():
                return None
            else:
                raise ApiError.from_error(e)

    def update(self, customer_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a customer

        Args:
            customer_id: Customer ID
            data: Update data

        Returns:
            Updated customer object

        Raises:
            ApiError: If customer not found or API error occurs
        """
        try:
            r = self.api.update(customer_id, data)

            if isinstance(r, dict) and "customer" in r:
                return r["customer"]
            else:
                return r
        except Exception as e:
            raise ApiError.from_error(e)

    def delete(self, customer_id: str) -> Dict[str, Any]:
        """
        Delete a customer

        Args:
            customer_id: Customer ID

        Returns:
            Deletion response

        Raises:
            ApiError: If customer not found or API error occurs
        """
        try:
            response = self.api.delete(customer_id)
            return response.get("accepted", False)
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


class CustomerClass:
    """Class-level access to Customer functionality and enums"""

    @property
    def KycStatus(self):
        try:
            from .models import KycStatus

            return KycStatus
        except ImportError:

            class MockKycStatus:
                APPROVED = "APPROVED"
                DENIED = "DENIED"
                IN_REVIEW = "IN_REVIEW"
                NOT_SUBMITTED = "NOT_SUBMITTED"

            return MockKycStatus

    @property
    def PaymentAuthorizationStatus(self):
        try:
            from .models import PaymentAuthorizationStatus

            return PaymentAuthorizationStatus
        except ImportError:

            class MockPaymentAuthorizationStatus:
                AUTHORIZED = "AUTHORIZED"
                NOT_AUTHORIZED = "NOT_AUTHORIZED"

            return MockPaymentAuthorizationStatus


Customer.KycStatus = CustomerClass().KycStatus
Customer.PaymentAuthorizationStatus = CustomerClass().PaymentAuthorizationStatus
