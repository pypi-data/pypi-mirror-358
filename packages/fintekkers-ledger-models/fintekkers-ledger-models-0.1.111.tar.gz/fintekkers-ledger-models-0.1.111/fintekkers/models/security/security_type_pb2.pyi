from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from typing import ClassVar as _ClassVar

DESCRIPTOR: _descriptor.FileDescriptor

class SecurityTypeProto(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UNKNOWN_SECURITY_TYPE: _ClassVar[SecurityTypeProto]
    CASH_SECURITY: _ClassVar[SecurityTypeProto]
    EQUITY_SECURITY: _ClassVar[SecurityTypeProto]
    BOND_SECURITY: _ClassVar[SecurityTypeProto]
    TIPS: _ClassVar[SecurityTypeProto]
    FRN: _ClassVar[SecurityTypeProto]
UNKNOWN_SECURITY_TYPE: SecurityTypeProto
CASH_SECURITY: SecurityTypeProto
EQUITY_SECURITY: SecurityTypeProto
BOND_SECURITY: SecurityTypeProto
TIPS: SecurityTypeProto
FRN: SecurityTypeProto
