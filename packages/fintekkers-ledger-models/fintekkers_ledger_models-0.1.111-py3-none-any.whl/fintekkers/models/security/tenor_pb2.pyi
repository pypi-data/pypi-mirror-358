from fintekkers.models.security import tenor_type_pb2 as _tenor_type_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TenorProto(_message.Message):
    __slots__ = ("object_class", "version", "term_value", "tenor_type")
    OBJECT_CLASS_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    TERM_VALUE_FIELD_NUMBER: _ClassVar[int]
    TENOR_TYPE_FIELD_NUMBER: _ClassVar[int]
    object_class: str
    version: str
    term_value: str
    tenor_type: _tenor_type_pb2.TenorTypeProto
    def __init__(self, object_class: _Optional[str] = ..., version: _Optional[str] = ..., term_value: _Optional[str] = ..., tenor_type: _Optional[_Union[_tenor_type_pb2.TenorTypeProto, str]] = ...) -> None: ...
