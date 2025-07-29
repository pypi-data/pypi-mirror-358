from fintekkers.models.position import field_pb2 as _field_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetFieldsResponseProto(_message.Message):
    __slots__ = ("object_class", "version", "fields")
    OBJECT_CLASS_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    FIELDS_FIELD_NUMBER: _ClassVar[int]
    object_class: str
    version: str
    fields: _containers.RepeatedScalarFieldContainer[_field_pb2.FieldProto]
    def __init__(self, object_class: _Optional[str] = ..., version: _Optional[str] = ..., fields: _Optional[_Iterable[_Union[_field_pb2.FieldProto, str]]] = ...) -> None: ...
