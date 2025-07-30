# jamm_sdk/webhook.py
import json
import hmac
import hashlib
from typing import Dict, Any, Optional, Union


# ========== Exception Classes ==========


class InvalidSignatureError(Exception):
    """Raised when webhook signature verification fails"""

    pass


# ========== Webhook Message Classes ==========


class WebhookMessage:
    """Represents a parsed webhook message (equivalent to MerchantWebhookMessage)"""

    def __init__(self, data: Dict[str, Any]):
        self.id = data.get("id")
        self.signature = data.get("signature")
        self.created_at = data.get("created_at")
        self.event_type = data.get("event_type")
        self.content = data.get("content", {})  # Will be replaced by parse() method
        self._raw_data = data

    def __repr__(self):
        return f"WebhookMessage(id={self.id}, event_type={self.event_type})"


class ChargeMessage:
    """Represents a charge webhook message content (equivalent to ChargeMessage)"""

    def __init__(self, data: Dict[str, Any]):
        self.id = data.get("id")
        self.customer = data.get("customer")
        self.description = data.get("description")
        self.merchant_name = data.get("merchant_name")
        self.initial_amount = data.get("initial_amount")
        self.discount = data.get("discount")
        self.final_amount = data.get("final_amount")
        self.currency = data.get("currency")
        self.processed_at = data.get("processed_at")
        self.created_at = data.get("created_at")
        self.updated_at = data.get("updated_at")
        self.error = data.get("error")  # For failed charges
        self._raw_data = data

    def __repr__(self):
        return f"ChargeMessage(id={self.id}, amount={self.final_amount})"


class ContractMessage:
    """Represents a contract webhook message content"""

    def __init__(self, data: Dict[str, Any]):
        self.customer = data.get("customer")
        self.created_at = data.get("created_at")
        self.activated_at = data.get("activated_at")
        self.merchant_name = data.get("merchant_name")
        self._raw_data = data

    def __repr__(self):
        return f"ContractMessage(customer={self.customer})"


# ========== Webhook Class ==========


class Webhook:
    """High-level webhook operations and message parsing"""

    def __init__(self, api_client=None):
        # Keep minimal initialization for consistency with other classes
        pass

    @staticmethod
    def parse(webhook_data: Union[Dict[str, Any], str]) -> WebhookMessage:
        """
        Parse command is for parsing the received webhook message.
        It does not call anything remotely, instead returns the suitable object.

        Args:
            webhook_data: Webhook message data (dict or JSON string)

        Returns:
            WebhookMessage object with parsed content

        Raises:
            ValueError: If event type is unknown
        """
        if isinstance(webhook_data, str):
            webhook_data = json.loads(webhook_data)

        # Create the main webhook message
        out = WebhookMessage(webhook_data)

        event_type = webhook_data.get("event_type")
        content = webhook_data.get("content", {})

        # Parse content based on event type
        if event_type in [
            "EVENT_TYPE_CHARGE_CREATED",
            "EVENT_TYPE_CHARGE_UPDATED",
            "EVENT_TYPE_CHARGE_CANCEL",
            "EVENT_TYPE_CHARGE_SUCCESS",
            "EVENT_TYPE_CHARGE_FAIL",
        ]:
            out.content = ChargeMessage(content)
            return out
        elif event_type == "EVENT_TYPE_CONTRACT_ACTIVATED":
            out.content = ContractMessage(content)
            return out
        else:
            raise ValueError("Unknown event type")

    @staticmethod
    def verify(data: Dict[str, Any], signature: str, client_secret: str) -> None:
        """
        Verify webhook message signature

        Args:
            data: Webhook data to verify
            signature: Expected signature from webhook headers
            client_secret: Client secret for verification

        Raises:
            ValueError: If data or signature is None
            InvalidSignatureError: If signatures don't match
        """
        if data is None:
            raise ValueError("data cannot be None")
        if signature is None:
            raise ValueError("signature cannot be None")

        # Convert the data to JSON string
        json_string = json.dumps(data, separators=(",", ":"), sort_keys=True)

        # Calculate expected signature
        digest = hmac.new(
            client_secret.encode("utf-8"), json_string.encode("utf-8"), hashlib.sha256
        ).hexdigest()
        expected = f"sha256={digest}"

        # Return early if signatures match
        if Webhook.secure_compare(expected, signature):
            return

        # Raise error if they don't match
        raise InvalidSignatureError("Digests do not match")

    @staticmethod
    def secure_compare(a: str, b: str) -> bool:
        """
        Securely compare two strings of equal length.
        This method is a port of ActiveSupport::SecurityUtils.secure_compare
        which works on non-Rails platforms.

        Args:
            a: First string
            b: Second string

        Returns:
            True if strings are equal, False otherwise
        """
        if len(a) != len(b):
            return False

        # Convert strings to bytes
        a_bytes = a.encode("utf-8")
        b_bytes = b.encode("utf-8")
        result = 0

        # XOR each byte and accumulate the result
        for x, y in zip(a_bytes, b_bytes):
            result |= x ^ y

        return result == 0


# Make sure all classes are available at module level
__all__ = [
    "Webhook",
    "WebhookMessage",
    "ChargeMessage",
    "ContractMessage",
    "InvalidSignatureError",
]
