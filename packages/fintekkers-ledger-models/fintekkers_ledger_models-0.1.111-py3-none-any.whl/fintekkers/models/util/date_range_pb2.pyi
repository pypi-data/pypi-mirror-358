from fintekkers.models.util import local_timestamp_pb2 as _local_timestamp_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class DateRangeProto(_message.Message):
    __slots__ = ("object_class", "version", "start", "end")
    OBJECT_CLASS_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    START_FIELD_NUMBER: _ClassVar[int]
    END_FIELD_NUMBER: _ClassVar[int]
    object_class: str
    version: str
    start: _local_timestamp_pb2.LocalTimestampProto
    end: _local_timestamp_pb2.LocalTimestampProto
    def __init__(self, object_class: _Optional[str] = ..., version: _Optional[str] = ..., start: _Optional[_Union[_local_timestamp_pb2.LocalTimestampProto, _Mapping]] = ..., end: _Optional[_Union[_local_timestamp_pb2.LocalTimestampProto, _Mapping]] = ...) -> None: ...
