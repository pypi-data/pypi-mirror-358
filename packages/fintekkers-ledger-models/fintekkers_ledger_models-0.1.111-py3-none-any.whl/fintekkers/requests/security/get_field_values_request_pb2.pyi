from fintekkers.models.position import field_pb2 as _field_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetFieldValuesRequestProto(_message.Message):
    __slots__ = ("object_class", "version", "field")
    OBJECT_CLASS_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    FIELD_FIELD_NUMBER: _ClassVar[int]
    object_class: str
    version: str
    field: _field_pb2.FieldProto
    def __init__(self, object_class: _Optional[str] = ..., version: _Optional[str] = ..., field: _Optional[_Union[_field_pb2.FieldProto, str]] = ...) -> None: ...
