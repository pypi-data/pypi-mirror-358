from typing import Dict, Any, Optional, Tuple
from .client import ApiClient


class HealthcheckApi:
    """Healthcheck API operations"""

    def __init__(self, api_client: Optional[ApiClient] = None):
        self.api_client = api_client or ApiClient()

    def ping(self, **kwargs) -> Dict[str, Any]:
        """Ping Jamm server to check connection"""
        data, status_code, headers = self.ping_with_http_info(**kwargs)
        return data

    def ping_with_http_info(self, **kwargs) -> Tuple[Any, int, Dict]:
        """Ping with full HTTP info"""
        opts = {"return_type": "object", "accepts": ["application/json"], **kwargs}
        return self.api_client.call_api("GET", "/v1/healthcheck", opts)
