from buf.validate import validate_pb2 as _validate_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Gender(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    GENDER_UNSPECIFIED: _ClassVar[Gender]
    GENDER_FEMALE: _ClassVar[Gender]
    GENDER_MALE: _ClassVar[Gender]
    GENDER_UNKNOWN: _ClassVar[Gender]

class CommonStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    COMMON_STATUS_UNSPECIFIED: _ClassVar[CommonStatus]
    COMMON_STATUS_INITIAL: _ClassVar[CommonStatus]
    COMMON_STATUS_ACTIVATED: _ClassVar[CommonStatus]
    COMMON_STATUS_DEACTIVATED: _ClassVar[CommonStatus]
    COMMON_STATUS_BLOCKING: _ClassVar[CommonStatus]

class ChargeStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    CHARGE_STATUS_UNSPECIFIED: _ClassVar[ChargeStatus]
    CHARGE_STATUS_SUCCESS: _ClassVar[ChargeStatus]
    CHARGE_STATUS_FAILURE: _ClassVar[ChargeStatus]
    CHARGE_STATUS_WAITING_EKYC: _ClassVar[ChargeStatus]
    CHARGE_STATUS_BLOCKING: _ClassVar[ChargeStatus]
    CHARGE_STATUS_CANCELLED: _ClassVar[ChargeStatus]
    CHARGE_STATUS_REFUNDED: _ClassVar[ChargeStatus]

class JammUserAgreementName(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    JAMM_USER_AGREEMENT_NAME_UNSPECIFIED: _ClassVar[JammUserAgreementName]
    JAMM_USER_AGREEMENT_NAME_PRIVACY_POLICY: _ClassVar[JammUserAgreementName]
    JAMM_USER_AGREEMENT_NAME_TERMS_OF_SERVICE: _ClassVar[JammUserAgreementName]

class KycState(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    KYC_STATE_UNSPECIFIED: _ClassVar[KycState]
    KYC_STATE_ACCEPTED: _ClassVar[KycState]
    KYC_STATE_PLANS_SELECTED: _ClassVar[KycState]
    KYC_STATE_DOCUMENT_SUBMITTED: _ClassVar[KycState]
    KYC_STATE_IN_PROGRESS: _ClassVar[KycState]
    KYC_STATE_VERIFIED: _ClassVar[KycState]
    KYC_STATE_NOT_STARTED: _ClassVar[KycState]
    KYC_STATE_DENIED: _ClassVar[KycState]

class KycResult(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    KYC_RESULT_UNSPECIFIED: _ClassVar[KycResult]
    KYC_RESULT_APPROVED: _ClassVar[KycResult]
    KYC_RESULT_DENIED: _ClassVar[KycResult]

class RefundStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    REFUND_STATUS_UNSPECIFIED: _ClassVar[RefundStatus]
    REFUND_STATUS_WAITING_CONFIRMATION: _ClassVar[RefundStatus]
    REFUND_STATUS_CONFIRMED: _ClassVar[RefundStatus]
    REFUND_STATUS_FAILED: _ClassVar[RefundStatus]
    REFUND_STATUS_CANCELED_BY_MERCHANT: _ClassVar[RefundStatus]

class RejectReason(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    REJECT_REASON_UNSPECIFIED: _ClassVar[RejectReason]
    REJECT_REASON_MERCHANT_REQUEST_DENIED: _ClassVar[RejectReason]
    REJECT_REASON_NEGATIVE_MERCHANT_BALANCE: _ClassVar[RejectReason]
    REJECT_REASON_PAYMENT_REJECTED_BY_BANK: _ClassVar[RejectReason]

GENDER_UNSPECIFIED: Gender
GENDER_FEMALE: Gender
GENDER_MALE: Gender
GENDER_UNKNOWN: Gender
COMMON_STATUS_UNSPECIFIED: CommonStatus
COMMON_STATUS_INITIAL: CommonStatus
COMMON_STATUS_ACTIVATED: CommonStatus
COMMON_STATUS_DEACTIVATED: CommonStatus
COMMON_STATUS_BLOCKING: CommonStatus
CHARGE_STATUS_UNSPECIFIED: ChargeStatus
CHARGE_STATUS_SUCCESS: ChargeStatus
CHARGE_STATUS_FAILURE: ChargeStatus
CHARGE_STATUS_WAITING_EKYC: ChargeStatus
CHARGE_STATUS_BLOCKING: ChargeStatus
CHARGE_STATUS_CANCELLED: ChargeStatus
CHARGE_STATUS_REFUNDED: ChargeStatus
JAMM_USER_AGREEMENT_NAME_UNSPECIFIED: JammUserAgreementName
JAMM_USER_AGREEMENT_NAME_PRIVACY_POLICY: JammUserAgreementName
JAMM_USER_AGREEMENT_NAME_TERMS_OF_SERVICE: JammUserAgreementName
KYC_STATE_UNSPECIFIED: KycState
KYC_STATE_ACCEPTED: KycState
KYC_STATE_PLANS_SELECTED: KycState
KYC_STATE_DOCUMENT_SUBMITTED: KycState
KYC_STATE_IN_PROGRESS: KycState
KYC_STATE_VERIFIED: KycState
KYC_STATE_NOT_STARTED: KycState
KYC_STATE_DENIED: KycState
KYC_RESULT_UNSPECIFIED: KycResult
KYC_RESULT_APPROVED: KycResult
KYC_RESULT_DENIED: KycResult
REFUND_STATUS_UNSPECIFIED: RefundStatus
REFUND_STATUS_WAITING_CONFIRMATION: RefundStatus
REFUND_STATUS_CONFIRMED: RefundStatus
REFUND_STATUS_FAILED: RefundStatus
REFUND_STATUS_CANCELED_BY_MERCHANT: RefundStatus
REJECT_REASON_UNSPECIFIED: RejectReason
REJECT_REASON_MERCHANT_REQUEST_DENIED: RejectReason
REJECT_REASON_NEGATIVE_MERCHANT_BALANCE: RejectReason
REJECT_REASON_PAYMENT_REJECTED_BY_BANK: RejectReason

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

class Buyer(_message.Message):
    __slots__ = (
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

    EMAIL_FIELD_NUMBER: _ClassVar[int]
    FORCE_KYC_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    KATAKANA_LAST_NAME_FIELD_NUMBER: _ClassVar[int]
    KATAKANA_FIRST_NAME_FIELD_NUMBER: _ClassVar[int]
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    BIRTH_DATE_FIELD_NUMBER: _ClassVar[int]
    GENDER_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
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

class Kyc(_message.Message):
    __slots__ = ("public_id", "state", "result")
    PUBLIC_ID_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    public_id: str
    state: KycState
    result: KycResult
    def __init__(
        self,
        public_id: _Optional[str] = ...,
        state: _Optional[_Union[KycState, str]] = ...,
        result: _Optional[_Union[KycResult, str]] = ...,
    ) -> None: ...

class DateFilter(_message.Message):
    __slots__ = ("range", "exact_date")
    RANGE_FIELD_NUMBER: _ClassVar[int]
    EXACT_DATE_FIELD_NUMBER: _ClassVar[int]
    range: DateRange
    exact_date: _timestamp_pb2.Timestamp
    def __init__(
        self,
        range: _Optional[_Union[DateRange, _Mapping]] = ...,
        exact_date: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...,
    ) -> None: ...

class DateRange(_message.Message):
    __slots__ = ("start_date", "end_date")
    START_DATE_FIELD_NUMBER: _ClassVar[int]
    END_DATE_FIELD_NUMBER: _ClassVar[int]
    start_date: _timestamp_pb2.Timestamp
    end_date: _timestamp_pb2.Timestamp
    def __init__(
        self,
        start_date: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...,
        end_date: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...,
    ) -> None: ...

class UserAgreements(_message.Message):
    __slots__ = ("jamm_user_agreement",)
    JAMM_USER_AGREEMENT_FIELD_NUMBER: _ClassVar[int]
    jamm_user_agreement: JammUserAgreement
    def __init__(
        self, jamm_user_agreement: _Optional[_Union[JammUserAgreement, _Mapping]] = ...
    ) -> None: ...

class JammUserAgreement(_message.Message):
    __slots__ = ("customer_id", "agreement_name", "agreed_at")
    CUSTOMER_ID_FIELD_NUMBER: _ClassVar[int]
    AGREEMENT_NAME_FIELD_NUMBER: _ClassVar[int]
    AGREED_AT_FIELD_NUMBER: _ClassVar[int]
    customer_id: str
    agreement_name: JammUserAgreementName
    agreed_at: _timestamp_pb2.Timestamp
    def __init__(
        self,
        customer_id: _Optional[str] = ...,
        agreement_name: _Optional[_Union[JammUserAgreementName, str]] = ...,
        agreed_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...,
    ) -> None: ...

class TrustdockData(_message.Message):
    __slots__ = (
        "id",
        "public_id",
        "state",
        "result",
        "accepted_at",
        "plans_selected_at",
        "document_submitted_at",
        "prepared_at",
        "verified_at",
        "records",
    )
    ID_FIELD_NUMBER: _ClassVar[int]
    PUBLIC_ID_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    ACCEPTED_AT_FIELD_NUMBER: _ClassVar[int]
    PLANS_SELECTED_AT_FIELD_NUMBER: _ClassVar[int]
    DOCUMENT_SUBMITTED_AT_FIELD_NUMBER: _ClassVar[int]
    PREPARED_AT_FIELD_NUMBER: _ClassVar[int]
    VERIFIED_AT_FIELD_NUMBER: _ClassVar[int]
    RECORDS_FIELD_NUMBER: _ClassVar[int]
    id: str
    public_id: str
    state: str
    result: str
    accepted_at: _timestamp_pb2.Timestamp
    plans_selected_at: _timestamp_pb2.Timestamp
    document_submitted_at: _timestamp_pb2.Timestamp
    prepared_at: _timestamp_pb2.Timestamp
    verified_at: _timestamp_pb2.Timestamp
    records: _containers.RepeatedCompositeFieldContainer[Record]
    def __init__(
        self,
        id: _Optional[str] = ...,
        public_id: _Optional[str] = ...,
        state: _Optional[str] = ...,
        result: _Optional[str] = ...,
        accepted_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...,
        plans_selected_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...,
        document_submitted_at: _Optional[
            _Union[_timestamp_pb2.Timestamp, _Mapping]
        ] = ...,
        prepared_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...,
        verified_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...,
        records: _Optional[_Iterable[_Union[Record, _Mapping]]] = ...,
    ) -> None: ...

class Record(_message.Message):
    __slots__ = ("state", "result", "content", "verified_at")
    STATE_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    VERIFIED_AT_FIELD_NUMBER: _ClassVar[int]
    state: str
    result: str
    content: str
    verified_at: _timestamp_pb2.Timestamp
    def __init__(
        self,
        state: _Optional[str] = ...,
        result: _Optional[str] = ...,
        content: _Optional[str] = ...,
        verified_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...,
    ) -> None: ...
