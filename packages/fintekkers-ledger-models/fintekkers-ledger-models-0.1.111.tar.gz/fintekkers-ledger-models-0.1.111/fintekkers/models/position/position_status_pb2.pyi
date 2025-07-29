from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from typing import ClassVar as _ClassVar

DESCRIPTOR: _descriptor.FileDescriptor

class PositionStatusProto(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UNKNOWN: _ClassVar[PositionStatusProto]
    HYPOTHETICAL: _ClassVar[PositionStatusProto]
    INTENDED: _ClassVar[PositionStatusProto]
    EXECUTED: _ClassVar[PositionStatusProto]
UNKNOWN: PositionStatusProto
HYPOTHETICAL: PositionStatusProto
INTENDED: PositionStatusProto
EXECUTED: PositionStatusProto
