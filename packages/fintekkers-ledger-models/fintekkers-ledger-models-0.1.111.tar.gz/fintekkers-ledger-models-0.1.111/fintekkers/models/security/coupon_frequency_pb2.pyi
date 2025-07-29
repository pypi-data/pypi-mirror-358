from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from typing import ClassVar as _ClassVar

DESCRIPTOR: _descriptor.FileDescriptor

class CouponFrequencyProto(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UNKNOWN_COUPON_FREQUENCY: _ClassVar[CouponFrequencyProto]
    ANNUALLY: _ClassVar[CouponFrequencyProto]
    SEMIANNUALLY: _ClassVar[CouponFrequencyProto]
    QUARTERLY: _ClassVar[CouponFrequencyProto]
    MONTHLY: _ClassVar[CouponFrequencyProto]
    NO_COUPON: _ClassVar[CouponFrequencyProto]
UNKNOWN_COUPON_FREQUENCY: CouponFrequencyProto
ANNUALLY: CouponFrequencyProto
SEMIANNUALLY: CouponFrequencyProto
QUARTERLY: CouponFrequencyProto
MONTHLY: CouponFrequencyProto
NO_COUPON: CouponFrequencyProto
