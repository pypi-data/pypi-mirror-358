from enum import Enum


class EnvironmentType(str, Enum):
    PRODUCTION = "production"
    PROD = "prod"
    PRD = "prd"
    LOCAL = "local"
    # Allow any other environment string

    @classmethod
    def _missing_(cls, value):
        # Allow any environment string
        # This makes the Enum accept any value
        return value


class Environment:
    """Environment settings for Jamm SDK"""

    version = "0.1.0"

    def __init__(self, env=None):
        """
        Initialize environment

        Args:
            env: String environment name ('production', 'local', or custom env name)
        """
        self.type = env or "production"

        # Set environment-specific URLs
        if self.type in (
            EnvironmentType.PRODUCTION,
            EnvironmentType.PROD,
            EnvironmentType.PRD,
        ):
            self.oauth_base = "https://merchant-identity.jamm-pay.jp"
            self.api_host = "api.jamm-pay.jp"
            self.verify_ssl = True
        elif self.type == EnvironmentType.LOCAL:
            self.oauth_base = "https://merchant-identity.develop.jamm-pay.jp"
            self.api_host = "api.jamm.test"
            self.verify_ssl = False
        else:
            # Custom environment (staging, develop, etc.)
            self.oauth_base = f"https://merchant-identity.{self.type}.jamm-pay.jp"
            self.api_host = f"api.{self.type}.jamm-pay.jp"
            self.verify_ssl = True
