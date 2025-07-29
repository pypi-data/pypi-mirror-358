from fintekkers.models.position import position_util_pb2 as _position_util_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class PositionFilterProto(_message.Message):
    __slots__ = ("object_class", "version", "filters")
    OBJECT_CLASS_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    FILTERS_FIELD_NUMBER: _ClassVar[int]
    object_class: str
    version: str
    filters: _containers.RepeatedCompositeFieldContainer[_position_util_pb2.FieldMapEntry]
    def __init__(self, object_class: _Optional[str] = ..., version: _Optional[str] = ..., filters: _Optional[_Iterable[_Union[_position_util_pb2.FieldMapEntry, _Mapping]]] = ...) -> None: ...
