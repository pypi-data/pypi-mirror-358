from typing import Optional, Type, TypeVar
from google.protobuf.message import Message

from .auth.oauth import OAuthHandler
from .config.settings import ClientConfig
from .http.client import HTTPClient
from .environment.env import Environment
from .api.client import ApiClient, Configuration as ApiConfiguration
from .customer import Customer
from .contract import Contract
from .charge import Charge
from .payment import Payment
from .bank import Bank, BankBranch
from .healthcheck import Healthcheck

T = TypeVar("T", bound=Message)


class JammClient:
    """Main client for interacting with the Jamm API."""

    def __init__(self, config=None, client_id=None, client_secret=None, env=None):
        """
        Initialize the Jamm client

        Args:
            config: Optional ClientConfig instance
            client_id: API client ID (overrides config value)
            client_secret: API client secret (overrides config value)
            env: Environment name ('production', 'local', or custom)
        """
        # Initialize configuration
        self.config = config or ClientConfig()

        # Override config with explicit parameters if provided
        if client_id:
            self.config.client_id = client_id
        if client_secret:
            self.config.client_secret = client_secret
        if env:
            self.config.environment = env

        # Set up environment
        self.environment = Environment(self.config.environment)

        # Update config with environment URLs
        self.config.oauth_base_url = self.environment.oauth_base
        self.config.verify_ssl = self.environment.verify_ssl

        # Initialize auth handler
        self.auth = OAuthHandler(self.config, self.environment)

        # Initialize HTTP client
        self.http = HTTPClient(self.auth, self.environment)

        # Initialize API client
        api_config = ApiConfiguration(host=self.environment.api_host)
        api_config.verify_ssl = self.environment.verify_ssl
        self.api_client = ApiClient(api_config)

        # Set up authentication for ApiClient
        self.api_client.config.auth_settings["oauth2"] = {
            "in": "header",
            "key": "Authorization",
            "value": lambda: f"Bearer {self.auth._ensure_token()}",
        }

    @classmethod
    def configure(cls, client_id, client_secret, env="production"):
        """
        Configure and create a new client instance

        Args:
            client_id: API client ID
            client_secret: API client secret
            env: Environment name ('production', 'local', or custom)

        Returns:
            Configured JammClient instance
        """
        return cls(client_id=client_id, client_secret=client_secret, env=env)

    def healthcheck(self):
        """Simple healthcheck endpoint"""
        response = self.http.request("GET", "/v1/healthcheck")
        return response

    # High-level convenience methods
    @property
    def customers(self):
        """Access to customer operations"""
        # Return an INSTANCE initialized with the API client, not the class itself
        return Customer(self.api_client)

    @property
    def contracts(self):
        """Access to contract operations"""
        return Contract(self.api_client)

    @property
    def charges(self):
        """Access to charge operations"""
        return Charge(self.api_client)

    @property
    def payments(self):
        """Access to payment operations"""
        return Payment(self.api_client)

    @property
    def banks(self):
        """Access to bank operations"""
        return Bank(self.api_client)

    @property
    def bank_branches(self):
        """Access to bank branch operations"""
        return BankBranch(self.api_client)

    def ping(self):
        """Quick ping using high-level wrapper"""
        return self.healthcheck()
