from api.v1 import common_pb2 as _common_pb2
from buf.validate import validate_pb2 as _validate_pb2
from google.api import annotations_pb2 as _annotations_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from protoc_gen_openapiv2.options import annotations_pb2 as _annotations_pb2_1
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class OnSessionPaymentErrorCode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ON_SESSION_PAYMENT_ERROR_CODE_UNSPECIFIED: _ClassVar[OnSessionPaymentErrorCode]
    ON_SESSION_PAYMENT_ERROR_CODE_MISSING_REDIRECT_URLS: _ClassVar[
        OnSessionPaymentErrorCode
    ]
    ON_SESSION_PAYMENT_ERROR_CODE_MISSING_REQUIRED_PARAMETERS: _ClassVar[
        OnSessionPaymentErrorCode
    ]
    ON_SESSION_PAYMENT_ERROR_CODE_MISSING_CHARGE: _ClassVar[OnSessionPaymentErrorCode]
    ON_SESSION_PAYMENT_ERROR_CODE_CUSTOMER_NOT_FOUND: _ClassVar[
        OnSessionPaymentErrorCode
    ]
    ON_SESSION_PAYMENT_ERROR_CODE_CUSTOMER_INACTIVE: _ClassVar[
        OnSessionPaymentErrorCode
    ]
    ON_SESSION_PAYMENT_ERROR_CODE_MERCHANT_CUSTOMER_ALREADY_EXISTS: _ClassVar[
        OnSessionPaymentErrorCode
    ]
    ON_SESSION_PAYMENT_ERROR_CODE_VALIDATION_FAILED: _ClassVar[
        OnSessionPaymentErrorCode
    ]
    ON_SESSION_PAYMENT_ERROR_CODE_STRATEGY_EXECUTION_FAILED: _ClassVar[
        OnSessionPaymentErrorCode
    ]
    ON_SESSION_PAYMENT_ERROR_CODE_INVALID_PAYMENT_STRATEGY: _ClassVar[
        OnSessionPaymentErrorCode
    ]

ON_SESSION_PAYMENT_ERROR_CODE_UNSPECIFIED: OnSessionPaymentErrorCode
ON_SESSION_PAYMENT_ERROR_CODE_MISSING_REDIRECT_URLS: OnSessionPaymentErrorCode
ON_SESSION_PAYMENT_ERROR_CODE_MISSING_REQUIRED_PARAMETERS: OnSessionPaymentErrorCode
ON_SESSION_PAYMENT_ERROR_CODE_MISSING_CHARGE: OnSessionPaymentErrorCode
ON_SESSION_PAYMENT_ERROR_CODE_CUSTOMER_NOT_FOUND: OnSessionPaymentErrorCode
ON_SESSION_PAYMENT_ERROR_CODE_CUSTOMER_INACTIVE: OnSessionPaymentErrorCode
ON_SESSION_PAYMENT_ERROR_CODE_MERCHANT_CUSTOMER_ALREADY_EXISTS: (
    OnSessionPaymentErrorCode
)
ON_SESSION_PAYMENT_ERROR_CODE_VALIDATION_FAILED: OnSessionPaymentErrorCode
ON_SESSION_PAYMENT_ERROR_CODE_STRATEGY_EXECUTION_FAILED: OnSessionPaymentErrorCode
ON_SESSION_PAYMENT_ERROR_CODE_INVALID_PAYMENT_STRATEGY: OnSessionPaymentErrorCode

class OffSessionPaymentRequest(_message.Message):
    __slots__ = ("customer", "charge")
    CUSTOMER_FIELD_NUMBER: _ClassVar[int]
    CHARGE_FIELD_NUMBER: _ClassVar[int]
    customer: str
    charge: InitialCharge
    def __init__(
        self,
        customer: _Optional[str] = ...,
        charge: _Optional[_Union[InitialCharge, _Mapping]] = ...,
    ) -> None: ...

class OffSessionPaymentResponse(_message.Message):
    __slots__ = ("customer", "charge")
    CUSTOMER_FIELD_NUMBER: _ClassVar[int]
    CHARGE_FIELD_NUMBER: _ClassVar[int]
    customer: _common_pb2.Customer
    charge: ChargeResult
    def __init__(
        self,
        customer: _Optional[_Union[_common_pb2.Customer, _Mapping]] = ...,
        charge: _Optional[_Union[ChargeResult, _Mapping]] = ...,
    ) -> None: ...

class AddChargeRequest(_message.Message):
    __slots__ = ("customer", "charge", "redirect")
    CUSTOMER_FIELD_NUMBER: _ClassVar[int]
    CHARGE_FIELD_NUMBER: _ClassVar[int]
    REDIRECT_FIELD_NUMBER: _ClassVar[int]
    customer: str
    charge: InitialCharge
    redirect: URL
    def __init__(
        self,
        customer: _Optional[str] = ...,
        charge: _Optional[_Union[InitialCharge, _Mapping]] = ...,
        redirect: _Optional[_Union[URL, _Mapping]] = ...,
    ) -> None: ...

class AddChargeResponse(_message.Message):
    __slots__ = ("charge", "customer", "payment_link")
    CHARGE_FIELD_NUMBER: _ClassVar[int]
    CUSTOMER_FIELD_NUMBER: _ClassVar[int]
    PAYMENT_LINK_FIELD_NUMBER: _ClassVar[int]
    charge: Charge
    customer: _common_pb2.Customer
    payment_link: PaymentLink
    def __init__(
        self,
        charge: _Optional[_Union[Charge, _Mapping]] = ...,
        customer: _Optional[_Union[_common_pb2.Customer, _Mapping]] = ...,
        payment_link: _Optional[_Union[PaymentLink, _Mapping]] = ...,
    ) -> None: ...

class GetChargesRequest(_message.Message):
    __slots__ = ("customer", "pagination")
    CUSTOMER_FIELD_NUMBER: _ClassVar[int]
    PAGINATION_FIELD_NUMBER: _ClassVar[int]
    customer: str
    pagination: _common_pb2.Pagination
    def __init__(
        self,
        customer: _Optional[str] = ...,
        pagination: _Optional[_Union[_common_pb2.Pagination, _Mapping]] = ...,
    ) -> None: ...

class GetChargesResponse(_message.Message):
    __slots__ = ("charges", "customer", "pagination")
    CHARGES_FIELD_NUMBER: _ClassVar[int]
    CUSTOMER_FIELD_NUMBER: _ClassVar[int]
    PAGINATION_FIELD_NUMBER: _ClassVar[int]
    charges: _containers.RepeatedCompositeFieldContainer[ChargeResult]
    customer: _common_pb2.Customer
    pagination: _common_pb2.Pagination
    def __init__(
        self,
        charges: _Optional[_Iterable[_Union[ChargeResult, _Mapping]]] = ...,
        customer: _Optional[_Union[_common_pb2.Customer, _Mapping]] = ...,
        pagination: _Optional[_Union[_common_pb2.Pagination, _Mapping]] = ...,
    ) -> None: ...

class GetChargeRequest(_message.Message):
    __slots__ = ("charge",)
    CHARGE_FIELD_NUMBER: _ClassVar[int]
    charge: str
    def __init__(self, charge: _Optional[str] = ...) -> None: ...

class GetChargeResponse(_message.Message):
    __slots__ = ("charge", "customer")
    CHARGE_FIELD_NUMBER: _ClassVar[int]
    CUSTOMER_FIELD_NUMBER: _ClassVar[int]
    charge: ChargeResult
    customer: _common_pb2.Customer
    def __init__(
        self,
        charge: _Optional[_Union[ChargeResult, _Mapping]] = ...,
        customer: _Optional[_Union[_common_pb2.Customer, _Mapping]] = ...,
    ) -> None: ...

class WithdrawRequest(_message.Message):
    __slots__ = ("customer", "charge")
    CUSTOMER_FIELD_NUMBER: _ClassVar[int]
    CHARGE_FIELD_NUMBER: _ClassVar[int]
    customer: str
    charge: InitialCharge
    def __init__(
        self,
        customer: _Optional[str] = ...,
        charge: _Optional[_Union[InitialCharge, _Mapping]] = ...,
    ) -> None: ...

class WithdrawResponse(_message.Message):
    __slots__ = ("customer", "charge")
    CUSTOMER_FIELD_NUMBER: _ClassVar[int]
    CHARGE_FIELD_NUMBER: _ClassVar[int]
    customer: _common_pb2.Customer
    charge: ChargeResult
    def __init__(
        self,
        customer: _Optional[_Union[_common_pb2.Customer, _Mapping]] = ...,
        charge: _Optional[_Union[ChargeResult, _Mapping]] = ...,
    ) -> None: ...

class CreateContractWithoutChargeRequest(_message.Message):
    __slots__ = ("buyer", "redirect")
    BUYER_FIELD_NUMBER: _ClassVar[int]
    REDIRECT_FIELD_NUMBER: _ClassVar[int]
    buyer: _common_pb2.Buyer
    redirect: URL
    def __init__(
        self,
        buyer: _Optional[_Union[_common_pb2.Buyer, _Mapping]] = ...,
        redirect: _Optional[_Union[URL, _Mapping]] = ...,
    ) -> None: ...

class CreateContractWithoutChargeResponse(_message.Message):
    __slots__ = ("contract", "customer", "payment_link")
    CONTRACT_FIELD_NUMBER: _ClassVar[int]
    CUSTOMER_FIELD_NUMBER: _ClassVar[int]
    PAYMENT_LINK_FIELD_NUMBER: _ClassVar[int]
    contract: _common_pb2.Contract
    customer: _common_pb2.Customer
    payment_link: PaymentLink
    def __init__(
        self,
        contract: _Optional[_Union[_common_pb2.Contract, _Mapping]] = ...,
        customer: _Optional[_Union[_common_pb2.Customer, _Mapping]] = ...,
        payment_link: _Optional[_Union[PaymentLink, _Mapping]] = ...,
    ) -> None: ...

class CreateContractWithChargeRequest(_message.Message):
    __slots__ = ("buyer", "charge", "redirect")
    BUYER_FIELD_NUMBER: _ClassVar[int]
    CHARGE_FIELD_NUMBER: _ClassVar[int]
    REDIRECT_FIELD_NUMBER: _ClassVar[int]
    buyer: _common_pb2.Buyer
    charge: InitialCharge
    redirect: URL
    def __init__(
        self,
        buyer: _Optional[_Union[_common_pb2.Buyer, _Mapping]] = ...,
        charge: _Optional[_Union[InitialCharge, _Mapping]] = ...,
        redirect: _Optional[_Union[URL, _Mapping]] = ...,
    ) -> None: ...

class CreateContractWithChargeResponse(_message.Message):
    __slots__ = ("contract", "charge", "customer", "payment_link")
    CONTRACT_FIELD_NUMBER: _ClassVar[int]
    CHARGE_FIELD_NUMBER: _ClassVar[int]
    CUSTOMER_FIELD_NUMBER: _ClassVar[int]
    PAYMENT_LINK_FIELD_NUMBER: _ClassVar[int]
    contract: _common_pb2.Contract
    charge: Charge
    customer: _common_pb2.Customer
    payment_link: PaymentLink
    def __init__(
        self,
        contract: _Optional[_Union[_common_pb2.Contract, _Mapping]] = ...,
        charge: _Optional[_Union[Charge, _Mapping]] = ...,
        customer: _Optional[_Union[_common_pb2.Customer, _Mapping]] = ...,
        payment_link: _Optional[_Union[PaymentLink, _Mapping]] = ...,
    ) -> None: ...

class URL(_message.Message):
    __slots__ = ("success_url", "failure_url")
    SUCCESS_URL_FIELD_NUMBER: _ClassVar[int]
    FAILURE_URL_FIELD_NUMBER: _ClassVar[int]
    success_url: str
    failure_url: str
    def __init__(
        self, success_url: _Optional[str] = ..., failure_url: _Optional[str] = ...
    ) -> None: ...

class InitialCharge(_message.Message):
    __slots__ = ("price", "description", "metadata", "expires_at")

    class MetadataEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(
            self, key: _Optional[str] = ..., value: _Optional[str] = ...
        ) -> None: ...

    PRICE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    EXPIRES_AT_FIELD_NUMBER: _ClassVar[int]
    price: int
    description: str
    metadata: _containers.ScalarMap[str, str]
    expires_at: _timestamp_pb2.Timestamp
    def __init__(
        self,
        price: _Optional[int] = ...,
        description: _Optional[str] = ...,
        metadata: _Optional[_Mapping[str, str]] = ...,
        expires_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...,
    ) -> None: ...

class Charge(_message.Message):
    __slots__ = ("id", "price", "description", "metadata", "expires_at")

    class MetadataEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(
            self, key: _Optional[str] = ..., value: _Optional[str] = ...
        ) -> None: ...

    ID_FIELD_NUMBER: _ClassVar[int]
    PRICE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    EXPIRES_AT_FIELD_NUMBER: _ClassVar[int]
    id: str
    price: int
    description: str
    metadata: _containers.ScalarMap[str, str]
    expires_at: _timestamp_pb2.Timestamp
    def __init__(
        self,
        id: _Optional[str] = ...,
        price: _Optional[int] = ...,
        description: _Optional[str] = ...,
        metadata: _Optional[_Mapping[str, str]] = ...,
        expires_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...,
    ) -> None: ...

class ChargeResult(_message.Message):
    __slots__ = (
        "charge_id",
        "paid",
        "reason",
        "description",
        "merchant_name",
        "initial_amount",
        "discount",
        "final_amount",
        "amount_refunded",
        "currency",
        "token_id",
        "metadata",
        "created_at",
        "updated_at",
        "processed_at",
    )

    class MetadataEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(
            self, key: _Optional[str] = ..., value: _Optional[str] = ...
        ) -> None: ...

    CHARGE_ID_FIELD_NUMBER: _ClassVar[int]
    PAID_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    MERCHANT_NAME_FIELD_NUMBER: _ClassVar[int]
    INITIAL_AMOUNT_FIELD_NUMBER: _ClassVar[int]
    DISCOUNT_FIELD_NUMBER: _ClassVar[int]
    FINAL_AMOUNT_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_REFUNDED_FIELD_NUMBER: _ClassVar[int]
    CURRENCY_FIELD_NUMBER: _ClassVar[int]
    TOKEN_ID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    PROCESSED_AT_FIELD_NUMBER: _ClassVar[int]
    charge_id: str
    paid: bool
    reason: str
    description: str
    merchant_name: str
    initial_amount: int
    discount: int
    final_amount: int
    amount_refunded: int
    currency: str
    token_id: str
    metadata: _containers.ScalarMap[str, str]
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    processed_at: _timestamp_pb2.Timestamp
    def __init__(
        self,
        charge_id: _Optional[str] = ...,
        paid: bool = ...,
        reason: _Optional[str] = ...,
        description: _Optional[str] = ...,
        merchant_name: _Optional[str] = ...,
        initial_amount: _Optional[int] = ...,
        discount: _Optional[int] = ...,
        final_amount: _Optional[int] = ...,
        amount_refunded: _Optional[int] = ...,
        currency: _Optional[str] = ...,
        token_id: _Optional[str] = ...,
        metadata: _Optional[_Mapping[str, str]] = ...,
        created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...,
        updated_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...,
        processed_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...,
    ) -> None: ...

class PaymentLink(_message.Message):
    __slots__ = ("url", "created_at", "expires_at")
    URL_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    EXPIRES_AT_FIELD_NUMBER: _ClassVar[int]
    url: str
    created_at: _timestamp_pb2.Timestamp
    expires_at: _timestamp_pb2.Timestamp
    def __init__(
        self,
        url: _Optional[str] = ...,
        created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...,
        expires_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...,
    ) -> None: ...

class OnSessionPaymentRequest(_message.Message):
    __slots__ = ("customer", "buyer", "charge", "redirect")
    CUSTOMER_FIELD_NUMBER: _ClassVar[int]
    BUYER_FIELD_NUMBER: _ClassVar[int]
    CHARGE_FIELD_NUMBER: _ClassVar[int]
    REDIRECT_FIELD_NUMBER: _ClassVar[int]
    customer: str
    buyer: _common_pb2.Buyer
    charge: InitialCharge
    redirect: URL
    def __init__(
        self,
        customer: _Optional[str] = ...,
        buyer: _Optional[_Union[_common_pb2.Buyer, _Mapping]] = ...,
        charge: _Optional[_Union[InitialCharge, _Mapping]] = ...,
        redirect: _Optional[_Union[URL, _Mapping]] = ...,
    ) -> None: ...

class OnSessionPaymentError(_message.Message):
    __slots__ = ("code", "message")
    CODE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    code: OnSessionPaymentErrorCode
    message: str
    def __init__(
        self,
        code: _Optional[_Union[OnSessionPaymentErrorCode, str]] = ...,
        message: _Optional[str] = ...,
    ) -> None: ...

class OnSessionPaymentData(_message.Message):
    __slots__ = ("contract", "charge", "customer", "payment_link")
    CONTRACT_FIELD_NUMBER: _ClassVar[int]
    CHARGE_FIELD_NUMBER: _ClassVar[int]
    CUSTOMER_FIELD_NUMBER: _ClassVar[int]
    PAYMENT_LINK_FIELD_NUMBER: _ClassVar[int]
    contract: _common_pb2.Contract
    charge: Charge
    customer: _common_pb2.Customer
    payment_link: PaymentLink
    def __init__(
        self,
        contract: _Optional[_Union[_common_pb2.Contract, _Mapping]] = ...,
        charge: _Optional[_Union[Charge, _Mapping]] = ...,
        customer: _Optional[_Union[_common_pb2.Customer, _Mapping]] = ...,
        payment_link: _Optional[_Union[PaymentLink, _Mapping]] = ...,
    ) -> None: ...

class OnSessionPaymentResponse(_message.Message):
    __slots__ = ("success", "error", "data")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    success: bool
    error: OnSessionPaymentError
    data: OnSessionPaymentData
    def __init__(
        self,
        success: bool = ...,
        error: _Optional[_Union[OnSessionPaymentError, _Mapping]] = ...,
        data: _Optional[_Union[OnSessionPaymentData, _Mapping]] = ...,
    ) -> None: ...
