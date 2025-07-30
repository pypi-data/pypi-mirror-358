"""Customer models for Jamm SDK."""

from lib.proto.api.v1.customer_pb2 import (
    CreateCustomerRequest as _CreateCustomerRequest,
    CreateCustomerResponse as _CreateCustomerResponse,
    GetCustomerRequest as _GetCustomerRequest,
    GetCustomerResponse as _GetCustomerResponse,
    UpdateCustomerRequest as _UpdateCustomerRequest,
    UpdateCustomerResponse as _UpdateCustomerResponse,
    DeleteCustomerRequest as _DeleteCustomerRequest,
    DeleteCustomerResponse as _DeleteCustomerResponse,
    GetContractRequest as _GetContractRequest,
    GetContractResponse as _GetContractResponse,
)

# Direct re-exports
CreateCustomerRequest = _CreateCustomerRequest
CreateCustomerResponse = _CreateCustomerResponse
GetCustomerRequest = _GetCustomerRequest
GetCustomerResponse = _GetCustomerResponse
UpdateCustomerRequest = _UpdateCustomerRequest
UpdateCustomerResponse = _UpdateCustomerResponse
DeleteCustomerRequest = _DeleteCustomerRequest
DeleteCustomerResponse = _DeleteCustomerResponse
GetContractRequest = _GetContractRequest
GetContractResponse = _GetContractResponse
