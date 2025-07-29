from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from typing import ClassVar as _ClassVar

DESCRIPTOR: _descriptor.FileDescriptor

class CouponTypeProto(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UNKNOWN_COUPON_TYPE: _ClassVar[CouponTypeProto]
    FIXED: _ClassVar[CouponTypeProto]
    FLOAT: _ClassVar[CouponTypeProto]
    ZERO: _ClassVar[CouponTypeProto]
UNKNOWN_COUPON_TYPE: CouponTypeProto
FIXED: CouponTypeProto
FLOAT: CouponTypeProto
ZERO: CouponTypeProto
