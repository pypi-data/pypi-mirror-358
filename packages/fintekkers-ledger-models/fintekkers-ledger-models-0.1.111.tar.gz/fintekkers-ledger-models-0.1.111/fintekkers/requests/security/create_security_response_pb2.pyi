from fintekkers.models.security import security_pb2 as _security_pb2
from fintekkers.requests.security import create_security_request_pb2 as _create_security_request_pb2
from fintekkers.requests.util.errors import summary_pb2 as _summary_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CreateSecurityResponseProto(_message.Message):
    __slots__ = ("object_class", "version", "security_request", "security_response", "errors_or_warnings")
    OBJECT_CLASS_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    SECURITY_REQUEST_FIELD_NUMBER: _ClassVar[int]
    SECURITY_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    ERRORS_OR_WARNINGS_FIELD_NUMBER: _ClassVar[int]
    object_class: str
    version: str
    security_request: _create_security_request_pb2.CreateSecurityRequestProto
    security_response: _security_pb2.SecurityProto
    errors_or_warnings: _summary_pb2.SummaryProto
    def __init__(self, object_class: _Optional[str] = ..., version: _Optional[str] = ..., security_request: _Optional[_Union[_create_security_request_pb2.CreateSecurityRequestProto, _Mapping]] = ..., security_response: _Optional[_Union[_security_pb2.SecurityProto, _Mapping]] = ..., errors_or_warnings: _Optional[_Union[_summary_pb2.SummaryProto, _Mapping]] = ...) -> None: ...
