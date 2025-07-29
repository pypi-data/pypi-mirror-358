from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from typing import ClassVar as _ClassVar

DESCRIPTOR: _descriptor.FileDescriptor

class TenorTypeProto(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UNKNOWN_TENOR_TYPE: _ClassVar[TenorTypeProto]
    PERPETUAL: _ClassVar[TenorTypeProto]
    TERM: _ClassVar[TenorTypeProto]
UNKNOWN_TENOR_TYPE: TenorTypeProto
PERPETUAL: TenorTypeProto
TERM: TenorTypeProto
