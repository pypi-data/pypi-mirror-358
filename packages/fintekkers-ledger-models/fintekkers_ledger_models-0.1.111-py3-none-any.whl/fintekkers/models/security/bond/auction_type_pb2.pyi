from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from typing import ClassVar as _ClassVar

DESCRIPTOR: _descriptor.FileDescriptor

class AuctionTypeProto(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UNKNOWN_AUCTION_TYPE: _ClassVar[AuctionTypeProto]
    SINGLE_PRICE: _ClassVar[AuctionTypeProto]
UNKNOWN_AUCTION_TYPE: AuctionTypeProto
SINGLE_PRICE: AuctionTypeProto
