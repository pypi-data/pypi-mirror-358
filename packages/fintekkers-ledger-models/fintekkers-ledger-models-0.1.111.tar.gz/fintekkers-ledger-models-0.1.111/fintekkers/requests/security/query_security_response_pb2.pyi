from fintekkers.models.security import security_pb2 as _security_pb2
from fintekkers.requests.security import query_security_request_pb2 as _query_security_request_pb2
from fintekkers.requests.util.errors import summary_pb2 as _summary_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class QuerySecurityResponseProto(_message.Message):
    __slots__ = ("object_class", "version", "query_security_input", "security_response", "errors_or_warnings")
    OBJECT_CLASS_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    QUERY_SECURITY_INPUT_FIELD_NUMBER: _ClassVar[int]
    SECURITY_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    ERRORS_OR_WARNINGS_FIELD_NUMBER: _ClassVar[int]
    object_class: str
    version: str
    query_security_input: _query_security_request_pb2.QuerySecurityRequestProto
    security_response: _containers.RepeatedCompositeFieldContainer[_security_pb2.SecurityProto]
    errors_or_warnings: _containers.RepeatedCompositeFieldContainer[_summary_pb2.SummaryProto]
    def __init__(self, object_class: _Optional[str] = ..., version: _Optional[str] = ..., query_security_input: _Optional[_Union[_query_security_request_pb2.QuerySecurityRequestProto, _Mapping]] = ..., security_response: _Optional[_Iterable[_Union[_security_pb2.SecurityProto, _Mapping]]] = ..., errors_or_warnings: _Optional[_Iterable[_Union[_summary_pb2.SummaryProto, _Mapping]]] = ...) -> None: ...
