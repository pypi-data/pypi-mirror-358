from fintekkers.requests.util.errors import error_pb2 as _error_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SummaryProto(_message.Message):
    __slots__ = ("errors", "warnings")
    ERRORS_FIELD_NUMBER: _ClassVar[int]
    WARNINGS_FIELD_NUMBER: _ClassVar[int]
    errors: _containers.RepeatedCompositeFieldContainer[_error_pb2.ErrorProto]
    warnings: _containers.RepeatedCompositeFieldContainer[_error_pb2.WarningProto]
    def __init__(self, errors: _Optional[_Iterable[_Union[_error_pb2.ErrorProto, _Mapping]]] = ..., warnings: _Optional[_Iterable[_Union[_error_pb2.WarningProto, _Mapping]]] = ...) -> None: ...
