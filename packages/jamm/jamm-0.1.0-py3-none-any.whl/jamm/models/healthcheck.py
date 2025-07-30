"""Healthcheck models for Jamm SDK."""

from lib.proto.api.v1.healthcheck_pb2 import (
    PingRequest as _PingRequest,
    PingResponse as _PingResponse,
)

# Direct re-exports
PingRequest = _PingRequest
PingResponse = _PingResponse
