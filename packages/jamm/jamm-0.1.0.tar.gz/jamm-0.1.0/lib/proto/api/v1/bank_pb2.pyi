from api.v1 import common_pb2 as _common_pb2
from buf.validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetBankRequest(_message.Message):
    __slots__ = ("bank_code",)
    BANK_CODE_FIELD_NUMBER: _ClassVar[int]
    bank_code: str
    def __init__(self, bank_code: _Optional[str] = ...) -> None: ...

class GetBankResponse(_message.Message):
    __slots__ = ("bank",)
    BANK_FIELD_NUMBER: _ClassVar[int]
    bank: _common_pb2.Bank
    def __init__(
        self, bank: _Optional[_Union[_common_pb2.Bank, _Mapping]] = ...
    ) -> None: ...

class GetMajorBanksRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetMajorBanksResponse(_message.Message):
    __slots__ = ("mizuho", "mufg", "smbc")
    MIZUHO_FIELD_NUMBER: _ClassVar[int]
    MUFG_FIELD_NUMBER: _ClassVar[int]
    SMBC_FIELD_NUMBER: _ClassVar[int]
    mizuho: _common_pb2.Bank
    mufg: _common_pb2.Bank
    smbc: _common_pb2.Bank
    def __init__(
        self,
        mizuho: _Optional[_Union[_common_pb2.Bank, _Mapping]] = ...,
        mufg: _Optional[_Union[_common_pb2.Bank, _Mapping]] = ...,
        smbc: _Optional[_Union[_common_pb2.Bank, _Mapping]] = ...,
    ) -> None: ...

class SearchBanksRequest(_message.Message):
    __slots__ = ("query",)
    QUERY_FIELD_NUMBER: _ClassVar[int]
    query: str
    def __init__(self, query: _Optional[str] = ...) -> None: ...

class SearchBanksResponse(_message.Message):
    __slots__ = ("banks",)
    BANKS_FIELD_NUMBER: _ClassVar[int]
    banks: _containers.RepeatedCompositeFieldContainer[_common_pb2.Bank]
    def __init__(
        self, banks: _Optional[_Iterable[_Union[_common_pb2.Bank, _Mapping]]] = ...
    ) -> None: ...

class GetBranchRequest(_message.Message):
    __slots__ = ("bank_code", "branch_code")
    BANK_CODE_FIELD_NUMBER: _ClassVar[int]
    BRANCH_CODE_FIELD_NUMBER: _ClassVar[int]
    bank_code: str
    branch_code: str
    def __init__(
        self, bank_code: _Optional[str] = ..., branch_code: _Optional[str] = ...
    ) -> None: ...

class GetBranchResponse(_message.Message):
    __slots__ = ("branch",)
    BRANCH_FIELD_NUMBER: _ClassVar[int]
    branch: _common_pb2.BankBranch
    def __init__(
        self, branch: _Optional[_Union[_common_pb2.BankBranch, _Mapping]] = ...
    ) -> None: ...

class GetBranchesRequest(_message.Message):
    __slots__ = ("bank_code",)
    BANK_CODE_FIELD_NUMBER: _ClassVar[int]
    bank_code: str
    def __init__(self, bank_code: _Optional[str] = ...) -> None: ...

class GetBranchesResponse(_message.Message):
    __slots__ = ("branches",)
    BRANCHES_FIELD_NUMBER: _ClassVar[int]
    branches: _containers.RepeatedCompositeFieldContainer[_common_pb2.BankBranch]
    def __init__(
        self,
        branches: _Optional[_Iterable[_Union[_common_pb2.BankBranch, _Mapping]]] = ...,
    ) -> None: ...

class SearchBranchesRequest(_message.Message):
    __slots__ = ("bank_code", "query")
    BANK_CODE_FIELD_NUMBER: _ClassVar[int]
    QUERY_FIELD_NUMBER: _ClassVar[int]
    bank_code: str
    query: str
    def __init__(
        self, bank_code: _Optional[str] = ..., query: _Optional[str] = ...
    ) -> None: ...

class SearchBranchesResponse(_message.Message):
    __slots__ = ("branches",)
    BRANCHES_FIELD_NUMBER: _ClassVar[int]
    branches: _containers.RepeatedCompositeFieldContainer[_common_pb2.BankBranch]
    def __init__(
        self,
        branches: _Optional[_Iterable[_Union[_common_pb2.BankBranch, _Mapping]]] = ...,
    ) -> None: ...
