from buf.validate import validate_pb2 as _validate_pb2
from google.api import annotations_pb2 as _annotations_pb2
from google.protobuf import any_pb2 as _any_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class EventType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    EVENT_TYPE_UNSPECIFIED: _ClassVar[EventType]
    EVENT_TYPE_CHARGE_CREATED: _ClassVar[EventType]
    EVENT_TYPE_CHARGE_UPDATED: _ClassVar[EventType]
    EVENT_TYPE_CHARGE_SUCCESS: _ClassVar[EventType]
    EVENT_TYPE_CHARGE_FAIL: _ClassVar[EventType]
    EVENT_TYPE_CHARGE_CANCEL: _ClassVar[EventType]
    EVENT_TYPE_CONTRACT_ACTIVATED: _ClassVar[EventType]
    EVENT_TYPE_USER_ACCOUNT_DELETED: _ClassVar[EventType]
    EVENT_TYPE_TESTING: _ClassVar[EventType]

EVENT_TYPE_UNSPECIFIED: EventType
EVENT_TYPE_CHARGE_CREATED: EventType
EVENT_TYPE_CHARGE_UPDATED: EventType
EVENT_TYPE_CHARGE_SUCCESS: EventType
EVENT_TYPE_CHARGE_FAIL: EventType
EVENT_TYPE_CHARGE_CANCEL: EventType
EVENT_TYPE_CONTRACT_ACTIVATED: EventType
EVENT_TYPE_USER_ACCOUNT_DELETED: EventType
EVENT_TYPE_TESTING: EventType

class MessageRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class MessageResponse(_message.Message):
    __slots__ = (
        "merchant_webhook_message",
        "charge_message",
        "contract_message",
        "user_account_message",
    )
    MERCHANT_WEBHOOK_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    CHARGE_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    CONTRACT_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    USER_ACCOUNT_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    merchant_webhook_message: MerchantWebhookMessage
    charge_message: ChargeMessage
    contract_message: ContractMessage
    user_account_message: UserAccountMessage
    def __init__(
        self,
        merchant_webhook_message: _Optional[
            _Union[MerchantWebhookMessage, _Mapping]
        ] = ...,
        charge_message: _Optional[_Union[ChargeMessage, _Mapping]] = ...,
        contract_message: _Optional[_Union[ContractMessage, _Mapping]] = ...,
        user_account_message: _Optional[_Union[UserAccountMessage, _Mapping]] = ...,
    ) -> None: ...

class MerchantWebhookMessage(_message.Message):
    __slots__ = ("id", "signature", "event_type", "content", "created_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    SIGNATURE_FIELD_NUMBER: _ClassVar[int]
    EVENT_TYPE_FIELD_NUMBER: _ClassVar[int]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: str
    signature: str
    event_type: EventType
    content: _any_pb2.Any
    created_at: _timestamp_pb2.Timestamp
    def __init__(
        self,
        id: _Optional[str] = ...,
        signature: _Optional[str] = ...,
        event_type: _Optional[_Union[EventType, str]] = ...,
        content: _Optional[_Union[_any_pb2.Any, _Mapping]] = ...,
        created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...,
    ) -> None: ...

class ChargeMessage(_message.Message):
    __slots__ = (
        "id",
        "customer",
        "status",
        "description",
        "merchant_name",
        "initial_amount",
        "discount",
        "final_amount",
        "amount_refunded",
        "currency",
        "processed_at",
        "created_at",
        "updated_at",
        "error",
    )

    class Status(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        STATUS_UNSPECIFIED: _ClassVar[ChargeMessage.Status]
        STATUS_SUCCESS: _ClassVar[ChargeMessage.Status]
        STATUS_FAILURE: _ClassVar[ChargeMessage.Status]
        STATUS_WAITING_EKYC: _ClassVar[ChargeMessage.Status]
        STATUS_BLOCKING: _ClassVar[ChargeMessage.Status]
        STATUS_CANCELLED: _ClassVar[ChargeMessage.Status]

    STATUS_UNSPECIFIED: ChargeMessage.Status
    STATUS_SUCCESS: ChargeMessage.Status
    STATUS_FAILURE: ChargeMessage.Status
    STATUS_WAITING_EKYC: ChargeMessage.Status
    STATUS_BLOCKING: ChargeMessage.Status
    STATUS_CANCELLED: ChargeMessage.Status
    ID_FIELD_NUMBER: _ClassVar[int]
    CUSTOMER_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    MERCHANT_NAME_FIELD_NUMBER: _ClassVar[int]
    INITIAL_AMOUNT_FIELD_NUMBER: _ClassVar[int]
    DISCOUNT_FIELD_NUMBER: _ClassVar[int]
    FINAL_AMOUNT_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_REFUNDED_FIELD_NUMBER: _ClassVar[int]
    CURRENCY_FIELD_NUMBER: _ClassVar[int]
    PROCESSED_AT_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    id: str
    customer: str
    status: ChargeMessage.Status
    description: str
    merchant_name: str
    initial_amount: int
    discount: int
    final_amount: int
    amount_refunded: int
    currency: str
    processed_at: str
    created_at: str
    updated_at: str
    error: Error
    def __init__(
        self,
        id: _Optional[str] = ...,
        customer: _Optional[str] = ...,
        status: _Optional[_Union[ChargeMessage.Status, str]] = ...,
        description: _Optional[str] = ...,
        merchant_name: _Optional[str] = ...,
        initial_amount: _Optional[int] = ...,
        discount: _Optional[int] = ...,
        final_amount: _Optional[int] = ...,
        amount_refunded: _Optional[int] = ...,
        currency: _Optional[str] = ...,
        processed_at: _Optional[str] = ...,
        created_at: _Optional[str] = ...,
        updated_at: _Optional[str] = ...,
        error: _Optional[_Union[Error, _Mapping]] = ...,
    ) -> None: ...

class ContractMessage(_message.Message):
    __slots__ = ("customer", "created_at", "activated_at", "merchant_name")
    CUSTOMER_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    ACTIVATED_AT_FIELD_NUMBER: _ClassVar[int]
    MERCHANT_NAME_FIELD_NUMBER: _ClassVar[int]
    customer: str
    created_at: str
    activated_at: str
    merchant_name: str
    def __init__(
        self,
        customer: _Optional[str] = ...,
        created_at: _Optional[str] = ...,
        activated_at: _Optional[str] = ...,
        merchant_name: _Optional[str] = ...,
    ) -> None: ...

class UserAccountMessage(_message.Message):
    __slots__ = ("customer", "email", "deleted_at", "merchant_name")
    CUSTOMER_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    DELETED_AT_FIELD_NUMBER: _ClassVar[int]
    MERCHANT_NAME_FIELD_NUMBER: _ClassVar[int]
    customer: str
    email: str
    deleted_at: str
    merchant_name: str
    def __init__(
        self,
        customer: _Optional[str] = ...,
        email: _Optional[str] = ...,
        deleted_at: _Optional[str] = ...,
        merchant_name: _Optional[str] = ...,
    ) -> None: ...

class Error(_message.Message):
    __slots__ = ("code", "message")
    CODE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    code: str
    message: str
    def __init__(
        self, code: _Optional[str] = ..., message: _Optional[str] = ...
    ) -> None: ...
