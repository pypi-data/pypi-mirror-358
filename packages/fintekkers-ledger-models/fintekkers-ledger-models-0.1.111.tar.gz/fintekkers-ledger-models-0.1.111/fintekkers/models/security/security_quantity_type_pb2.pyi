from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from typing import ClassVar as _ClassVar

DESCRIPTOR: _descriptor.FileDescriptor

class SecurityQuantityTypeProto(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UNKNOWN_QUANTITY_TYPE: _ClassVar[SecurityQuantityTypeProto]
    ORIGINAL_FACE_VALUE: _ClassVar[SecurityQuantityTypeProto]
    NOTIONAL: _ClassVar[SecurityQuantityTypeProto]
    UNITS: _ClassVar[SecurityQuantityTypeProto]
UNKNOWN_QUANTITY_TYPE: SecurityQuantityTypeProto
ORIGINAL_FACE_VALUE: SecurityQuantityTypeProto
NOTIONAL: SecurityQuantityTypeProto
UNITS: SecurityQuantityTypeProto
