from buf.validate import validate_pb2 as _validate_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class DepositType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    DEPOSIT_TYPE_UNSPECIFIED: _ClassVar[DepositType]
    DEPOSIT_TYPE_SAVINGS: _ClassVar[DepositType]
    DEPOSIT_TYPE_CHECKING: _ClassVar[DepositType]

class PaymentAuthorizationStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    PAYMENT_AUTHORIZATION_STATUS_UNSPECIFIED: _ClassVar[PaymentAuthorizationStatus]
    PAYMENT_AUTHORIZATION_STATUS_AUTHORIZED: _ClassVar[PaymentAuthorizationStatus]
    PAYMENT_AUTHORIZATION_STATUS_NOT_AUTHORIZED: _ClassVar[PaymentAuthorizationStatus]

class KycStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    KYC_STATUS_UNSPECIFIED: _ClassVar[KycStatus]
    KYC_STATUS_APPROVED: _ClassVar[KycStatus]
    KYC_STATUS_NOT_SUBMITTED: _ClassVar[KycStatus]
    KYC_STATUS_IN_REVIEW: _ClassVar[KycStatus]
    KYC_STATUS_DENIED: _ClassVar[KycStatus]

class ContractStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    CONTRACT_STATUS_UNSPECIFIED: _ClassVar[ContractStatus]
    CONTRACT_STATUS_INITIAL: _ClassVar[ContractStatus]
    CONTRACT_STATUS_APPROVED: _ClassVar[ContractStatus]
    CONTRACT_STATUS_ACTIVATED: _ClassVar[ContractStatus]
    CONTRACT_STATUS_WAITING_EKYC: _ClassVar[ContractStatus]
    CONTRACT_STATUS_EXPIRED: _ClassVar[ContractStatus]
    CONTRACT_STATUS_DEACTIVATED: _ClassVar[ContractStatus]
    CONTRACT_STATUS_CANCELLED: _ClassVar[ContractStatus]
    CONTRACT_STATUS_PENDING_CHARGE: _ClassVar[ContractStatus]

DEPOSIT_TYPE_UNSPECIFIED: DepositType
DEPOSIT_TYPE_SAVINGS: DepositType
DEPOSIT_TYPE_CHECKING: DepositType
PAYMENT_AUTHORIZATION_STATUS_UNSPECIFIED: PaymentAuthorizationStatus
PAYMENT_AUTHORIZATION_STATUS_AUTHORIZED: PaymentAuthorizationStatus
PAYMENT_AUTHORIZATION_STATUS_NOT_AUTHORIZED: PaymentAuthorizationStatus
KYC_STATUS_UNSPECIFIED: KycStatus
KYC_STATUS_APPROVED: KycStatus
KYC_STATUS_NOT_SUBMITTED: KycStatus
KYC_STATUS_IN_REVIEW: KycStatus
KYC_STATUS_DENIED: KycStatus
CONTRACT_STATUS_UNSPECIFIED: ContractStatus
CONTRACT_STATUS_INITIAL: ContractStatus
CONTRACT_STATUS_APPROVED: ContractStatus
CONTRACT_STATUS_ACTIVATED: ContractStatus
CONTRACT_STATUS_WAITING_EKYC: ContractStatus
CONTRACT_STATUS_EXPIRED: ContractStatus
CONTRACT_STATUS_DEACTIVATED: ContractStatus
CONTRACT_STATUS_CANCELLED: ContractStatus
CONTRACT_STATUS_PENDING_CHARGE: ContractStatus

class Buyer(_message.Message):
    __slots__ = (
        "email",
        "force_kyc",
        "phone",
        "name",
        "katakana_last_name",
        "katakana_first_name",
        "address",
        "birth_date",
        "gender",
        "expires_at",
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

    EMAIL_FIELD_NUMBER: _ClassVar[int]
    FORCE_KYC_FIELD_NUMBER: _ClassVar[int]
    PHONE_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    KATAKANA_LAST_NAME_FIELD_NUMBER: _ClassVar[int]
    KATAKANA_FIRST_NAME_FIELD_NUMBER: _ClassVar[int]
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    BIRTH_DATE_FIELD_NUMBER: _ClassVar[int]
    GENDER_FIELD_NUMBER: _ClassVar[int]
    EXPIRES_AT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    email: str
    force_kyc: bool
    phone: str
    name: str
    katakana_last_name: str
    katakana_first_name: str
    address: str
    birth_date: str
    gender: str
    expires_at: _timestamp_pb2.Timestamp
    metadata: _containers.ScalarMap[str, str]
    def __init__(
        self,
        email: _Optional[str] = ...,
        force_kyc: bool = ...,
        phone: _Optional[str] = ...,
        name: _Optional[str] = ...,
        katakana_last_name: _Optional[str] = ...,
        katakana_first_name: _Optional[str] = ...,
        address: _Optional[str] = ...,
        birth_date: _Optional[str] = ...,
        gender: _Optional[str] = ...,
        expires_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...,
        metadata: _Optional[_Mapping[str, str]] = ...,
    ) -> None: ...

class MerchantCustomer(_message.Message):
    __slots__ = ("customer", "merchant")
    CUSTOMER_FIELD_NUMBER: _ClassVar[int]
    MERCHANT_FIELD_NUMBER: _ClassVar[int]
    customer: Customer
    merchant: Merchant
    def __init__(
        self,
        customer: _Optional[_Union[Customer, _Mapping]] = ...,
        merchant: _Optional[_Union[Merchant, _Mapping]] = ...,
    ) -> None: ...

class Customer(_message.Message):
    __slots__ = (
        "id",
        "email",
        "activated",
        "status",
        "bank_information",
        "created_at",
        "updated_at",
    )
    ID_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    ACTIVATED_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    BANK_INFORMATION_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: str
    email: str
    activated: bool
    status: Status
    bank_information: BankInformation
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    def __init__(
        self,
        id: _Optional[str] = ...,
        email: _Optional[str] = ...,
        activated: bool = ...,
        status: _Optional[_Union[Status, _Mapping]] = ...,
        bank_information: _Optional[_Union[BankInformation, _Mapping]] = ...,
        created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...,
        updated_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...,
    ) -> None: ...

class Status(_message.Message):
    __slots__ = ("payment", "kyc")
    PAYMENT_FIELD_NUMBER: _ClassVar[int]
    KYC_FIELD_NUMBER: _ClassVar[int]
    payment: PaymentAuthorizationStatus
    kyc: KycStatus
    def __init__(
        self,
        payment: _Optional[_Union[PaymentAuthorizationStatus, str]] = ...,
        kyc: _Optional[_Union[KycStatus, str]] = ...,
    ) -> None: ...

class BankInformation(_message.Message):
    __slots__ = ("account_number", "bank_name", "branch_name", "deposit_type")
    ACCOUNT_NUMBER_FIELD_NUMBER: _ClassVar[int]
    BANK_NAME_FIELD_NUMBER: _ClassVar[int]
    BRANCH_NAME_FIELD_NUMBER: _ClassVar[int]
    DEPOSIT_TYPE_FIELD_NUMBER: _ClassVar[int]
    account_number: str
    bank_name: str
    branch_name: str
    deposit_type: DepositType
    def __init__(
        self,
        account_number: _Optional[str] = ...,
        bank_name: _Optional[str] = ...,
        branch_name: _Optional[str] = ...,
        deposit_type: _Optional[_Union[DepositType, str]] = ...,
    ) -> None: ...

class Merchant(_message.Message):
    __slots__ = ("id", "name")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    def __init__(
        self, id: _Optional[str] = ..., name: _Optional[str] = ...
    ) -> None: ...

class Contract(_message.Message):
    __slots__ = ("id", "status", "created_at", "updated_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: str
    status: ContractStatus
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    def __init__(
        self,
        id: _Optional[str] = ...,
        status: _Optional[_Union[ContractStatus, str]] = ...,
        created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...,
        updated_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...,
    ) -> None: ...

class Pagination(_message.Message):
    __slots__ = ("page_size", "page_token")
    PAGE_SIZE_FIELD_NUMBER: _ClassVar[int]
    PAGE_TOKEN_FIELD_NUMBER: _ClassVar[int]
    page_size: int
    page_token: str
    def __init__(
        self, page_size: _Optional[int] = ..., page_token: _Optional[str] = ...
    ) -> None: ...

class Bank(_message.Message):
    __slots__ = (
        "code",
        "name",
        "name_katakana",
        "name_hiragana",
        "name_alphabet",
        "assets",
        "quota",
        "opening_hours",
        "bankpay_scheduled_maintenances",
        "bank_scheduled_maintenances",
        "registration_scheduled_maintenances",
        "bankpay_available",
        "bank_available",
        "registration_available",
        "operating",
    )
    CODE_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    NAME_KATAKANA_FIELD_NUMBER: _ClassVar[int]
    NAME_HIRAGANA_FIELD_NUMBER: _ClassVar[int]
    NAME_ALPHABET_FIELD_NUMBER: _ClassVar[int]
    ASSETS_FIELD_NUMBER: _ClassVar[int]
    QUOTA_FIELD_NUMBER: _ClassVar[int]
    OPENING_HOURS_FIELD_NUMBER: _ClassVar[int]
    BANKPAY_SCHEDULED_MAINTENANCES_FIELD_NUMBER: _ClassVar[int]
    BANK_SCHEDULED_MAINTENANCES_FIELD_NUMBER: _ClassVar[int]
    REGISTRATION_SCHEDULED_MAINTENANCES_FIELD_NUMBER: _ClassVar[int]
    BANKPAY_AVAILABLE_FIELD_NUMBER: _ClassVar[int]
    BANK_AVAILABLE_FIELD_NUMBER: _ClassVar[int]
    REGISTRATION_AVAILABLE_FIELD_NUMBER: _ClassVar[int]
    OPERATING_FIELD_NUMBER: _ClassVar[int]
    code: str
    name: str
    name_katakana: str
    name_hiragana: str
    name_alphabet: str
    assets: BankAssets
    quota: BankQuota
    opening_hours: str
    bankpay_scheduled_maintenances: _containers.RepeatedCompositeFieldContainer[
        BankScheduledMaintenancePeriod
    ]
    bank_scheduled_maintenances: _containers.RepeatedCompositeFieldContainer[
        BankScheduledMaintenancePeriod
    ]
    registration_scheduled_maintenances: _containers.RepeatedCompositeFieldContainer[
        BankScheduledMaintenancePeriod
    ]
    bankpay_available: bool
    bank_available: bool
    registration_available: bool
    operating: bool
    def __init__(
        self,
        code: _Optional[str] = ...,
        name: _Optional[str] = ...,
        name_katakana: _Optional[str] = ...,
        name_hiragana: _Optional[str] = ...,
        name_alphabet: _Optional[str] = ...,
        assets: _Optional[_Union[BankAssets, _Mapping]] = ...,
        quota: _Optional[_Union[BankQuota, _Mapping]] = ...,
        opening_hours: _Optional[str] = ...,
        bankpay_scheduled_maintenances: _Optional[
            _Iterable[_Union[BankScheduledMaintenancePeriod, _Mapping]]
        ] = ...,
        bank_scheduled_maintenances: _Optional[
            _Iterable[_Union[BankScheduledMaintenancePeriod, _Mapping]]
        ] = ...,
        registration_scheduled_maintenances: _Optional[
            _Iterable[_Union[BankScheduledMaintenancePeriod, _Mapping]]
        ] = ...,
        bankpay_available: bool = ...,
        bank_available: bool = ...,
        registration_available: bool = ...,
        operating: bool = ...,
    ) -> None: ...

class BankQuota(_message.Message):
    __slots__ = (
        "offline_purchase_limit_per_charge_with_kyc",
        "offline_purchase_limit_per_charge_without_kyc",
        "offline_purchase_limit_per_day_with_kyc",
        "offline_purchase_limit_per_day_without_kyc",
        "subscription_purchase_limit_per_charge_with_kyc",
        "subscription_purchase_limit_per_charge_without_kyc",
        "subscription_purchase_limit_per_day_with_kyc",
        "subscription_purchase_limit_per_day_without_kyc",
    )
    OFFLINE_PURCHASE_LIMIT_PER_CHARGE_WITH_KYC_FIELD_NUMBER: _ClassVar[int]
    OFFLINE_PURCHASE_LIMIT_PER_CHARGE_WITHOUT_KYC_FIELD_NUMBER: _ClassVar[int]
    OFFLINE_PURCHASE_LIMIT_PER_DAY_WITH_KYC_FIELD_NUMBER: _ClassVar[int]
    OFFLINE_PURCHASE_LIMIT_PER_DAY_WITHOUT_KYC_FIELD_NUMBER: _ClassVar[int]
    SUBSCRIPTION_PURCHASE_LIMIT_PER_CHARGE_WITH_KYC_FIELD_NUMBER: _ClassVar[int]
    SUBSCRIPTION_PURCHASE_LIMIT_PER_CHARGE_WITHOUT_KYC_FIELD_NUMBER: _ClassVar[int]
    SUBSCRIPTION_PURCHASE_LIMIT_PER_DAY_WITH_KYC_FIELD_NUMBER: _ClassVar[int]
    SUBSCRIPTION_PURCHASE_LIMIT_PER_DAY_WITHOUT_KYC_FIELD_NUMBER: _ClassVar[int]
    offline_purchase_limit_per_charge_with_kyc: int
    offline_purchase_limit_per_charge_without_kyc: int
    offline_purchase_limit_per_day_with_kyc: int
    offline_purchase_limit_per_day_without_kyc: int
    subscription_purchase_limit_per_charge_with_kyc: int
    subscription_purchase_limit_per_charge_without_kyc: int
    subscription_purchase_limit_per_day_with_kyc: int
    subscription_purchase_limit_per_day_without_kyc: int
    def __init__(
        self,
        offline_purchase_limit_per_charge_with_kyc: _Optional[int] = ...,
        offline_purchase_limit_per_charge_without_kyc: _Optional[int] = ...,
        offline_purchase_limit_per_day_with_kyc: _Optional[int] = ...,
        offline_purchase_limit_per_day_without_kyc: _Optional[int] = ...,
        subscription_purchase_limit_per_charge_with_kyc: _Optional[int] = ...,
        subscription_purchase_limit_per_charge_without_kyc: _Optional[int] = ...,
        subscription_purchase_limit_per_day_with_kyc: _Optional[int] = ...,
        subscription_purchase_limit_per_day_without_kyc: _Optional[int] = ...,
    ) -> None: ...

class BankScheduledMaintenancePeriod(_message.Message):
    __slots__ = (
        "bank_code",
        "start_at_jst",
        "end_at_jst",
        "start_at_utc",
        "end_at_utc",
    )
    BANK_CODE_FIELD_NUMBER: _ClassVar[int]
    START_AT_JST_FIELD_NUMBER: _ClassVar[int]
    END_AT_JST_FIELD_NUMBER: _ClassVar[int]
    START_AT_UTC_FIELD_NUMBER: _ClassVar[int]
    END_AT_UTC_FIELD_NUMBER: _ClassVar[int]
    bank_code: str
    start_at_jst: str
    end_at_jst: str
    start_at_utc: str
    end_at_utc: str
    def __init__(
        self,
        bank_code: _Optional[str] = ...,
        start_at_jst: _Optional[str] = ...,
        end_at_jst: _Optional[str] = ...,
        start_at_utc: _Optional[str] = ...,
        end_at_utc: _Optional[str] = ...,
    ) -> None: ...

class BankBranch(_message.Message):
    __slots__ = (
        "bank_code",
        "branch_code",
        "name",
        "name_katakana",
        "name_hiragana",
        "name_alphabet",
    )
    BANK_CODE_FIELD_NUMBER: _ClassVar[int]
    BRANCH_CODE_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    NAME_KATAKANA_FIELD_NUMBER: _ClassVar[int]
    NAME_HIRAGANA_FIELD_NUMBER: _ClassVar[int]
    NAME_ALPHABET_FIELD_NUMBER: _ClassVar[int]
    bank_code: str
    branch_code: str
    name: str
    name_katakana: str
    name_hiragana: str
    name_alphabet: str
    def __init__(
        self,
        bank_code: _Optional[str] = ...,
        branch_code: _Optional[str] = ...,
        name: _Optional[str] = ...,
        name_katakana: _Optional[str] = ...,
        name_hiragana: _Optional[str] = ...,
        name_alphabet: _Optional[str] = ...,
    ) -> None: ...

class BankAssets(_message.Message):
    __slots__ = ("bank_code", "logo_url_large", "logo_url_medium", "terms_url")
    BANK_CODE_FIELD_NUMBER: _ClassVar[int]
    LOGO_URL_LARGE_FIELD_NUMBER: _ClassVar[int]
    LOGO_URL_MEDIUM_FIELD_NUMBER: _ClassVar[int]
    TERMS_URL_FIELD_NUMBER: _ClassVar[int]
    bank_code: str
    logo_url_large: str
    logo_url_medium: str
    terms_url: str
    def __init__(
        self,
        bank_code: _Optional[str] = ...,
        logo_url_large: _Optional[str] = ...,
        logo_url_medium: _Optional[str] = ...,
        terms_url: _Optional[str] = ...,
    ) -> None: ...
