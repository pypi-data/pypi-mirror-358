"""Common models for Jamm SDK."""

from lib.proto.api.v1.common_pb2 import (
    Buyer as _Buyer,
    Customer as _Customer,
    MerchantCustomer as _MerchantCustomer,
    Contract as _Contract,
    Pagination as _Pagination,
    Status as _Status,
    BankInformation as _BankInformation,
    Merchant as _Merchant,
    # Enums
    DepositType as _DepositType,
    PaymentAuthorizationStatus as _PaymentAuthorizationStatus,
    KycStatus as _KycStatus,
    ContractStatus as _ContractStatus,
)


# Monkey-patch the Buyer class with additional methods
def get_metadata(self, key: str, default: str = None) -> str:
    """Get a metadata value."""
    return self.metadata.get(key, default)


def set_metadata(self, key: str, value: str) -> None:
    """Set a metadata value."""
    self.metadata[key] = value


# Add methods to the protobuf class
_Buyer.get_metadata = get_metadata
_Buyer.set_metadata = set_metadata

# Re-export as Buyer
Buyer = _Buyer

# Direct re-exports
Customer = _Customer
MerchantCustomer = _MerchantCustomer
Contract = _Contract
Pagination = _Pagination
Status = _Status
BankInformation = _BankInformation
Merchant = _Merchant

# Enum re-exports
DepositType = _DepositType
PaymentAuthorizationStatus = _PaymentAuthorizationStatus
KycStatus = _KycStatus
ContractStatus = _ContractStatus
