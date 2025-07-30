"""Banking models for Jamm SDK."""

# Import from updated proto locations
from lib.proto.api.v1.bank_pb2 import (
    # API Request/Response classes
    GetBankRequest as _GetBankRequest,
    GetBankResponse as _GetBankResponse,
    GetMajorBanksRequest as _GetMajorBanksRequest,
    GetMajorBanksResponse as _GetMajorBanksResponse,
    SearchBanksRequest as _SearchBanksRequest,
    SearchBanksResponse as _SearchBanksResponse,
    GetBranchRequest as _GetBranchRequest,
    GetBranchResponse as _GetBranchResponse,
    GetBranchesRequest as _GetBranchesRequest,
    GetBranchesResponse as _GetBranchesResponse,
    SearchBranchesRequest as _SearchBranchesRequest,
    SearchBranchesResponse as _SearchBranchesResponse,
)

from lib.proto.api.v1.common_pb2 import (
    # Entity models
    Bank as _Bank,
    BankQuota as _BankQuota,
    BankBranch as _BankBranch,
    BankAssets as _BankAssets,
)


# Direct re-exports
Bank = _Bank
BankQuota = _BankQuota
BankBranch = _BankBranch
BankAssets = _BankAssets

# API Request/Response re-exports
GetBankRequest = _GetBankRequest
GetBankResponse = _GetBankResponse
GetMajorBanksRequest = _GetMajorBanksRequest
GetMajorBanksResponse = _GetMajorBanksResponse
SearchBanksRequest = _SearchBanksRequest
SearchBanksResponse = _SearchBanksResponse
GetBranchRequest = _GetBranchRequest
GetBranchResponse = _GetBranchResponse
GetBranchesRequest = _GetBranchesRequest
GetBranchesResponse = _GetBranchesResponse
SearchBranchesRequest = _SearchBranchesRequest
SearchBranchesResponse = _SearchBranchesResponse
