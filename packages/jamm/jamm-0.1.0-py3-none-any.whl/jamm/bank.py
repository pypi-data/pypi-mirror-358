# jamm_sdk/bank.py
from typing import Dict, Any, List, Optional
from .api.bank_api import BankApi
from .api.client import ApiClient
from .errors import ApiError


class Bank:
    """High-level bank operations"""

    def __init__(self, api_client: Optional[ApiClient] = None):
        self.api = BankApi(api_client)

    def get(self, bank_code: str) -> Optional[Dict[str, Any]]:
        """
        Get a bank by code

        Args:
            bank_code: Bank code

        Returns:
            Bank data or None if not found
        """
        try:
            return self.api.get_bank(bank_code)
        except Exception as e:
            if hasattr(e, "status") and e.status == 404:
                return None
            elif hasattr(e, "code") and e.code == 404:
                return None
            elif "404" in str(e) or "not found" in str(e).lower():
                return None
            else:
                raise ApiError.from_error(e)

    def search(self, query: str) -> Dict[str, Any]:
        """
        Search for banks

        Args:
            query: Search query

        Returns:
            Object with bank identifiers as keys (e.g., "mizuho", "mufg", "smbc")
            and detailed bank information as values

        Raises:
            ApiError: If search fails
        """
        try:
            return self.api.search_banks(query)
        except Exception as e:
            raise ApiError.from_error(e)

    def get_major_banks(self) -> Dict[str, Any]:
        """
        Get list of major banks

        Returns:
            Dictionary with bank identifiers as keys (mizuho, mufg, smbc)

        Raises:
            ApiError: If retrieval fails
        """
        try:
            return self.api.get_major_banks()
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


class BankBranch:
    """High-level bank branch operations"""

    def __init__(self, api_client: Optional[ApiClient] = None):
        self.api = BankApi(api_client)

    def get(self, bank_code: str, branch_code: str) -> Optional[Dict[str, Any]]:
        """
        Get a bank branch

        Args:
            bank_code: Bank code
            branch_code: Branch code

        Returns:
            Branch data or None if not found
        """
        try:
            return self.api.get_branch(bank_code, branch_code)
        except Exception as e:
            if hasattr(e, "status") and e.status == 404:
                return None
            elif hasattr(e, "code") and e.code == 404:
                return None
            elif "404" in str(e) or "not found" in str(e).lower():
                return None
            else:
                raise ApiError.from_error(e)

    def search(self, bank_code: str, query: str) -> List[Dict[str, Any]]:
        """
        Search for bank branches

        Args:
            bank_code: Bank code
            query: Search query

        Returns:
            List of matching branches

        Raises:
            ApiError: If search fails
        """
        try:
            response = self.api.search_branches(bank_code, query)
            return response.get("branches", [])
        except Exception as e:
            raise ApiError.from_error(e)

    def list_for_bank(self, bank_code: str) -> List[Dict[str, Any]]:
        """
        Get all branches for a bank

        Args:
            bank_code: Bank code

        Returns:
            List of bank branches

        Raises:
            ApiError: If retrieval fails
        """
        try:
            response = self.api.get_branches(bank_code)
            return response.get("branches", [])
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
