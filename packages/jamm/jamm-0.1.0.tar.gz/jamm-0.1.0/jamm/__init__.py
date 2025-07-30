"""Jamm SDK for Python"""

from .import_hook import install

install()

from typing import Any, Dict
from .client import JammClient
from .customer import Customer
from .contract import Contract
from .charge import Charge
from .payment import Payment
from .healthcheck import Healthcheck
from .bank import Bank, BankBranch
from .webhook import (
    Webhook,
    InvalidSignatureError,
    WebhookMessage,
    ChargeMessage,
    ContractMessage,
)
from .errors import ApiError  # ← Add this import

# API clients for advanced usage
from .api import (
    ApiClient,
    CustomerApi,
    PaymentApi,
    HealthcheckApi,
    BankApi,
)

# Configuration and environment
from .config.settings import ClientConfig
from .environment.env import Environment

from .version import VERSION as __version__


def configure(env: str, client_id: str, client_secret: str):
    """Configure and return a JammClient instance"""
    return JammClient.configure(client_id, client_secret, env)


# Main public API - high-level classes
__all__ = [
    # Main client and configuration
    "JammClient",
    "configure",
    # High-level operation classes
    "Customer",
    "Contract",
    "Charge",
    "Payment",
    "Healthcheck",
    "Bank",
    "BankBranch",
    "Webhook",
    # Webhook message classes
    "WebhookMessage",
    "ChargeMessage",
    "ContractMessage",
    # Exceptions
    "InvalidSignatureError",
    "ApiError",
    # Advanced API clients
    "ApiClient",
    "CustomerApi",
    "PaymentApi",
    "HealthcheckApi",
    "BankApi",
    # Configuration
    "ClientConfig",
    "Environment",
    # Version
    "__version__",
]


# Convenience methods for quick setup
def ping() -> Dict[str, Any]:
    """Quick healthcheck ping"""
    return Healthcheck.ping()
