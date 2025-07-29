from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from typing import ClassVar as _ClassVar

DESCRIPTOR: _descriptor.FileDescriptor

class MeasureProto(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UNKNOWN_MEASURE: _ClassVar[MeasureProto]
    DIRECTED_QUANTITY: _ClassVar[MeasureProto]
    MARKET_VALUE: _ClassVar[MeasureProto]
    UNADJUSTED_COST_BASIS: _ClassVar[MeasureProto]
    ADJUSTED_COST_BASIS: _ClassVar[MeasureProto]
    CURRENT_YIELD: _ClassVar[MeasureProto]
    YIELD_TO_MATURITY: _ClassVar[MeasureProto]
UNKNOWN_MEASURE: MeasureProto
DIRECTED_QUANTITY: MeasureProto
MARKET_VALUE: MeasureProto
UNADJUSTED_COST_BASIS: MeasureProto
ADJUSTED_COST_BASIS: MeasureProto
CURRENT_YIELD: MeasureProto
YIELD_TO_MATURITY: MeasureProto
