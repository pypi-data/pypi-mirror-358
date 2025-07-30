"""Payment models for Jamm SDK."""

# Import proto classes directly
from lib.proto.api.v1.payment_pb2 import (
    # Core models
    Charge as _Charge,
    URL as _URL,
    InitialCharge as _InitialCharge,
    PaymentLink as _PaymentLink,
    ChargeResult as _ChargeResult,
    # Request/Response classes
    AddChargeRequest as _AddChargeRequest,
    AddChargeResponse as _AddChargeResponse,
    CreateContractWithChargeRequest as _CreateContractWithChargeRequest,
    CreateContractWithChargeResponse as _CreateContractWithChargeResponse,
    CreateContractWithoutChargeRequest as _CreateContractWithoutChargeRequest,
    CreateContractWithoutChargeResponse as _CreateContractWithoutChargeResponse,
    GetChargeRequest as _GetChargeRequest,
    GetChargeResponse as _GetChargeResponse,
    GetChargesRequest as _GetChargesRequest,
    GetChargesResponse as _GetChargesResponse,
    OffSessionPaymentRequest as _OffSessionPaymentRequest,
    OffSessionPaymentResponse as _OffSessionPaymentResponse,
    WithdrawRequest as _WithdrawRequest,
    WithdrawResponse as _WithdrawResponse,
    OnSessionPaymentRequest as _OnSessionPaymentRequest,
    OnSessionPaymentResponse as _OnSessionPaymentResponse,
    OnSessionPaymentData as _OnSessionPaymentData,
    OnSessionPaymentError as _OnSessionPaymentError,
    # Enums
    OnSessionPaymentErrorCode as _OnSessionPaymentErrorCode,
)


# Monkey-patch the Charge class with additional methods
def get_metadata(self, key: str, default: str = None) -> str:
    """Get a metadata value."""
    return self.metadata.get(key, default)


def set_metadata(self, key: str, value: str) -> None:
    """Set a metadata value."""
    self.metadata[key] = value


# Add methods to the protobuf class
_Charge.get_metadata = get_metadata
_Charge.set_metadata = set_metadata

# Re-export as Charge
Charge = _Charge

# Direct re-exports for classes that don't need enhancement
URL = _URL
InitialCharge = _InitialCharge
PaymentLink = _PaymentLink
ChargeResult = _ChargeResult

# Request/Response classes - direct re-exports
AddChargeRequest = _AddChargeRequest
AddChargeResponse = _AddChargeResponse
CreateContractWithChargeRequest = _CreateContractWithChargeRequest
CreateContractWithChargeResponse = _CreateContractWithChargeResponse
CreateContractWithoutChargeRequest = _CreateContractWithoutChargeRequest
CreateContractWithoutChargeResponse = _CreateContractWithoutChargeResponse
GetChargeRequest = _GetChargeRequest
GetChargeResponse = _GetChargeResponse
GetChargesRequest = _GetChargesRequest
GetChargesResponse = _GetChargesResponse
OffSessionPaymentRequest = _OffSessionPaymentRequest
OffSessionPaymentResponse = _OffSessionPaymentResponse
WithdrawRequest = _WithdrawRequest
WithdrawResponse = _WithdrawResponse
OnSessionPaymentRequest = _OnSessionPaymentRequest
OnSessionPaymentResponse = _OnSessionPaymentResponse
OnSessionPaymentData = _OnSessionPaymentData
OnSessionPaymentError = _OnSessionPaymentError

# Enum re-export
OnSessionPaymentErrorCode = _OnSessionPaymentErrorCode
