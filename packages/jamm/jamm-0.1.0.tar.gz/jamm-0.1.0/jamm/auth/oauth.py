import time
import requests
from typing import Dict, Optional


class OAuthError(Exception):
    """Exception for OAuth-related errors"""

    pass


class OAuthHandler:
    """Handles OAuth authentication flow"""

    def __init__(self, config, environment):
        self.config = config
        self.environment = environment
        self.access_token = None
        self.token_expiry = 0

    def get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers for API requests"""
        token = self._ensure_token()
        if not token:
            return {}
        return {"Authorization": f"Bearer {token}"}

    def _ensure_token(self) -> Optional[str]:
        """Ensure we have a valid token, refreshing if needed"""
        if self.access_token is None or time.time() >= self.token_expiry:
            self._refresh_token()
        return self.access_token

    def _refresh_token(self):
        """Obtain a new OAuth token"""
        url = f"{self.environment.oauth_base}/oauth2/token"

        try:

            # Use form-encoded data instead of JSON
            response = requests.post(
                url,
                # Change this from json to data
                data={  # Changed from json to data
                    "grant_type": "client_credentials",
                    "client_id": self.config.client_id,
                    "client_secret": self.config.client_secret,
                },
                headers={
                    "Content-Type": "application/x-www-form-urlencoded"  # Add this header
                },
                timeout=self.config.timeout,
                verify=self.environment.verify_ssl,
            )

            if response.status_code == 200:
                data = response.json()
                self.access_token = data["access_token"]
                # Set token expiry (with 5min buffer)
                self.token_expiry = time.time() + data["expires_in"] - 300
            else:
                raise OAuthError(
                    f"Failed to obtain token: {response.status_code} - {response.text}"
                )
        except requests.RequestException as e:
            raise OAuthError(f"Token request failed: {str(e)}")
