from api.v1 import common_pb2 as _common_pb2
from buf.validate import validate_pb2 as _validate_pb2
from google.api import annotations_pb2 as _annotations_pb2
from protoc_gen_openapiv2.options import annotations_pb2 as _annotations_pb2_1
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CreateCustomerRequest(_message.Message):
    __slots__ = ("buyer",)
    BUYER_FIELD_NUMBER: _ClassVar[int]
    buyer: _common_pb2.Buyer
    def __init__(
        self, buyer: _Optional[_Union[_common_pb2.Buyer, _Mapping]] = ...
    ) -> None: ...

class CreateCustomerResponse(_message.Message):
    __slots__ = ("customer",)
    CUSTOMER_FIELD_NUMBER: _ClassVar[int]
    customer: _common_pb2.MerchantCustomer
    def __init__(
        self, customer: _Optional[_Union[_common_pb2.MerchantCustomer, _Mapping]] = ...
    ) -> None: ...

class GetCustomerRequest(_message.Message):
    __slots__ = ("customer",)
    CUSTOMER_FIELD_NUMBER: _ClassVar[int]
    customer: str
    def __init__(self, customer: _Optional[str] = ...) -> None: ...

class GetCustomerResponse(_message.Message):
    __slots__ = ("customer",)
    CUSTOMER_FIELD_NUMBER: _ClassVar[int]
    customer: _common_pb2.Customer
    def __init__(
        self, customer: _Optional[_Union[_common_pb2.Customer, _Mapping]] = ...
    ) -> None: ...

class UpdateCustomerRequest(_message.Message):
    __slots__ = (
        "customer",
        "email",
        "force_kyc",
        "name",
        "katakana_last_name",
        "katakana_first_name",
        "address",
        "birth_date",
        "gender",
        "metadata",
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

    CUSTOMER_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    FORCE_KYC_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    KATAKANA_LAST_NAME_FIELD_NUMBER: _ClassVar[int]
    KATAKANA_FIRST_NAME_FIELD_NUMBER: _ClassVar[int]
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    BIRTH_DATE_FIELD_NUMBER: _ClassVar[int]
    GENDER_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    customer: str
    email: str
    force_kyc: bool
    name: str
    katakana_last_name: str
    katakana_first_name: str
    address: str
    birth_date: str
    gender: str
    metadata: _containers.ScalarMap[str, str]
    def __init__(
        self,
        customer: _Optional[str] = ...,
        email: _Optional[str] = ...,
        force_kyc: bool = ...,
        name: _Optional[str] = ...,
        katakana_last_name: _Optional[str] = ...,
        katakana_first_name: _Optional[str] = ...,
        address: _Optional[str] = ...,
        birth_date: _Optional[str] = ...,
        gender: _Optional[str] = ...,
        metadata: _Optional[_Mapping[str, str]] = ...,
    ) -> None: ...

class UpdateCustomerResponse(_message.Message):
    __slots__ = ("customer",)
    CUSTOMER_FIELD_NUMBER: _ClassVar[int]
    customer: _common_pb2.MerchantCustomer
    def __init__(
        self, customer: _Optional[_Union[_common_pb2.MerchantCustomer, _Mapping]] = ...
    ) -> None: ...

class DeleteCustomerRequest(_message.Message):
    __slots__ = ("customer",)
    CUSTOMER_FIELD_NUMBER: _ClassVar[int]
    customer: str
    def __init__(self, customer: _Optional[str] = ...) -> None: ...

class DeleteCustomerResponse(_message.Message):
    __slots__ = ("accepted",)
    ACCEPTED_FIELD_NUMBER: _ClassVar[int]
    accepted: bool
    def __init__(self, accepted: bool = ...) -> None: ...

class GetContractRequest(_message.Message):
    __slots__ = ("customer",)
    CUSTOMER_FIELD_NUMBER: _ClassVar[int]
    customer: str
    def __init__(self, customer: _Optional[str] = ...) -> None: ...

class GetContractResponse(_message.Message):
    __slots__ = ("customer", "contract")
    CUSTOMER_FIELD_NUMBER: _ClassVar[int]
    CONTRACT_FIELD_NUMBER: _ClassVar[int]
    customer: _common_pb2.MerchantCustomer
    contract: _common_pb2.Contract
    def __init__(
        self,
        customer: _Optional[_Union[_common_pb2.MerchantCustomer, _Mapping]] = ...,
        contract: _Optional[_Union[_common_pb2.Contract, _Mapping]] = ...,
    ) -> None: ...
