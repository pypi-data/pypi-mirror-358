from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from typing import ClassVar as _ClassVar

DESCRIPTOR: _descriptor.FileDescriptor

class IdentifierTypeProto(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UNKNOWN_IDENTIFIER_TYPE: _ClassVar[IdentifierTypeProto]
    EXCH_TICKER: _ClassVar[IdentifierTypeProto]
    ISIN: _ClassVar[IdentifierTypeProto]
    CUSIP: _ClassVar[IdentifierTypeProto]
    OSI: _ClassVar[IdentifierTypeProto]
    FIGI: _ClassVar[IdentifierTypeProto]
    CASH: _ClassVar[IdentifierTypeProto]
UNKNOWN_IDENTIFIER_TYPE: IdentifierTypeProto
EXCH_TICKER: IdentifierTypeProto
ISIN: IdentifierTypeProto
CUSIP: IdentifierTypeProto
OSI: IdentifierTypeProto
FIGI: IdentifierTypeProto
CASH: IdentifierTypeProto
