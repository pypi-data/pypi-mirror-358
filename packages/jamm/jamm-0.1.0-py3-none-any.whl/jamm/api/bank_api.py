from typing import Dict, Any, Optional, Tuple
from .client import ApiClient
import requests


class BankApi:
    """Bank API operations for searching banks and branches"""

    def __init__(self, api_client: Optional[ApiClient] = None):
        self.api_client = api_client or ApiClient()

    def get_bank(self, bank_code: str, **kwargs) -> Dict[str, Any]:
        """Get a specific bank by code"""
        data, status_code, headers = self.get_bank_with_http_info(bank_code, **kwargs)
        return data

    def get_bank_with_http_info(
        self, bank_code: str, **kwargs
    ) -> Tuple[Any, int, Dict]:
        """Get bank with full HTTP info using gRPC-style endpoint"""
        # Create request body
        request_body = {"bankCode": bank_code}

        opts = {
            "return_type": "object",
            "auth_names": ["oauth2"],
            "accepts": ["application/json"],
            "content_types": ["application/json"],
            "body": request_body,
            **kwargs,
        }

        # Use the gRPC-style endpoint
        return self.api_client.call_api("POST", "/api.v1.BankService/GetBank", opts)

    def get_major_banks(self, **kwargs) -> Dict[str, Any]:
        """Get list of major banks"""
        data, status_code, headers = self.get_major_banks_with_http_info(**kwargs)
        return data

    def get_major_banks_with_http_info(self, **kwargs) -> Tuple[Any, int, Dict]:
        """Get major banks with full HTTP info"""
        # Make sure to provide an empty dict that will be sent as "{}"
        if "body" not in kwargs:
            kwargs["body"] = {}

        opts = {
            "return_type": "object",
            "auth_names": ["oauth2"],
            "accepts": ["application/json"],
            "content_types": ["application/json"],
            **kwargs,
        }
        return self.api_client.call_api(
            "POST", "/api.v1.BankService/GetMajorBanks", opts
        )

    def get_major_banks_direct(self) -> Dict[str, Any]:
        """Get major banks using direct request to avoid API client issues"""

        # Get auth token from the API client
        auth_header = {}
        if hasattr(self.api_client.config.auth_settings.get("oauth2", {}), "value"):
            token_fn = self.api_client.config.auth_settings["oauth2"].get("value")
            if callable(token_fn):
                auth_header = {"Authorization": token_fn()}

        # Make direct request
        response = requests.post(
            f"{self.api_client.config.scheme}://{self.api_client.config.host}/api.v1.BankService/GetMajorBanks",
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                **auth_header
            },
            json={},  # Empty JSON object
        )

        # Check for errors
        response.raise_for_status()

        # Return JSON response
        return response.json()

    def search_banks(self, query: str, **kwargs) -> Dict[str, Any]:
        """Search for banks"""
        data, status_code, headers = self.search_banks_with_http_info(query, **kwargs)
        return data

    def search_banks_with_http_info(
        self, query: str, **kwargs
    ) -> Tuple[Any, int, Dict]:
        """Search banks with full HTTP info"""
        # Move query param to request body
        request_body = {"query": query}

        opts = {
            "return_type": "object",
            "auth_names": ["oauth2"],
            "accepts": ["application/json"],
            "content_types": ["application/json"],
            "body": request_body,
            **kwargs,
        }
        return self.api_client.call_api("POST", "/api.v1.BankService/SearchBanks", opts)

    def get_branch(self, bank_code: str, branch_code: str, **kwargs) -> Dict[str, Any]:
        """Get a specific bank branch"""
        data, status_code, headers = self.get_branch_with_http_info(
            bank_code, branch_code, **kwargs
        )
        return data

    def get_branch_with_http_info(
        self, bank_code: str, branch_code: str, **kwargs
    ) -> Tuple[Any, int, Dict]:
        """Get branch with full HTTP info"""
        # Create request body with both codes
        request_body = {"bankCode": bank_code, "branchCode": branch_code}

        opts = {
            "return_type": "object",
            "auth_names": ["oauth2"],
            "accepts": ["application/json"],
            "content_types": ["application/json"],
            "body": request_body,
            **kwargs,
        }
        return self.api_client.call_api("POST", "/api.v1.BankService/GetBranch", opts)

    def get_branches(self, bank_code: str, **kwargs) -> Dict[str, Any]:
        """Get all branches for a bank"""
        data, status_code, headers = self.get_branches_with_http_info(
            bank_code, **kwargs
        )
        return data

    def get_branches_with_http_info(
        self, bank_code: str, **kwargs
    ) -> Tuple[Any, int, Dict]:
        """Get branches with full HTTP info"""
        # Create request body with bank code
        request_body = {"bankCode": bank_code}

        opts = {
            "return_type": "object",
            "auth_names": ["oauth2"],
            "accepts": ["application/json"],
            "content_types": ["application/json"],
            "body": request_body,
            **kwargs,
        }
        return self.api_client.call_api("POST", "/api.v1.BankService/GetBranches", opts)

    def search_branches(self, bank_code: str, query: str, **kwargs) -> Dict[str, Any]:
        """Search for bank branches"""
        data, status_code, headers = self.search_branches_with_http_info(
            bank_code, query, **kwargs
        )
        return data

    def search_branches_with_http_info(
        self, bank_code: str, query: str, **kwargs
    ) -> Tuple[Any, int, Dict]:
        """Search branches with full HTTP info"""
        # Move parameters to request body
        request_body = {"bankCode": bank_code, "query": query}

        opts = {
            "return_type": "object",
            "auth_names": ["oauth2"],
            "accepts": ["application/json"],
            "content_types": ["application/json"],
            "body": request_body,
            **kwargs,
        }
        return self.api_client.call_api(
            "POST", "/api.v1.BankService/SearchBranches", opts
        )
