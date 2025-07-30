from typing import Dict, Any, Optional
from .api.healthcheck_api import HealthcheckApi
from .api.client import ApiClient
from .errors import ApiError


class Healthcheck:
    """Health check operations"""

    def __init__(self, api_client: Optional[ApiClient] = None):
        self.api = HealthcheckApi(api_client)

    def ping(self) -> Dict[str, Any]:
        """
        Ping the Jamm server to check connectivity

        Returns:
            Healthcheck response

        Raises:
            ApiError: If ping fails
        """
        try:
            return self.api.ping()
        except Exception as e:
            raise ApiError.from_error(e)

    def check(self) -> bool:
        """
        Simple boolean health check

        Returns:
            True if service is healthy, False otherwise
        """
        try:
            self.ping()
            return True
        except Exception:
            return False

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
