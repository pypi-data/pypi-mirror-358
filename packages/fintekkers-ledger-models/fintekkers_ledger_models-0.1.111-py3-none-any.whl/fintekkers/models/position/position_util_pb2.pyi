from google.protobuf import any_pb2 as _any_pb2
from fintekkers.models.position import field_pb2 as _field_pb2
from fintekkers.models.position import measure_pb2 as _measure_pb2
from fintekkers.models.util import decimal_value_pb2 as _decimal_value_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class PositionFilterOperator(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UNKNOWN_OPERATOR: _ClassVar[PositionFilterOperator]
    EQUALS: _ClassVar[PositionFilterOperator]
    NOT_EQUALS: _ClassVar[PositionFilterOperator]
    LESS_THAN: _ClassVar[PositionFilterOperator]
    LESS_THAN_OR_EQUALS: _ClassVar[PositionFilterOperator]
    MORE_THAN: _ClassVar[PositionFilterOperator]
    MORE_THAN_OR_EQUALS: _ClassVar[PositionFilterOperator]
UNKNOWN_OPERATOR: PositionFilterOperator
EQUALS: PositionFilterOperator
NOT_EQUALS: PositionFilterOperator
LESS_THAN: PositionFilterOperator
LESS_THAN_OR_EQUALS: PositionFilterOperator
MORE_THAN: PositionFilterOperator
MORE_THAN_OR_EQUALS: PositionFilterOperator

class MeasureMapEntry(_message.Message):
    __slots__ = ("measure", "measure_decimal_value")
    MEASURE_FIELD_NUMBER: _ClassVar[int]
    MEASURE_DECIMAL_VALUE_FIELD_NUMBER: _ClassVar[int]
    measure: _measure_pb2.MeasureProto
    measure_decimal_value: _decimal_value_pb2.DecimalValueProto
    def __init__(self, measure: _Optional[_Union[_measure_pb2.MeasureProto, str]] = ..., measure_decimal_value: _Optional[_Union[_decimal_value_pb2.DecimalValueProto, _Mapping]] = ...) -> None: ...

class FieldMapEntry(_message.Message):
    __slots__ = ("field", "field_value_packed", "enum_value", "string_value", "operator")
    FIELD_FIELD_NUMBER: _ClassVar[int]
    FIELD_VALUE_PACKED_FIELD_NUMBER: _ClassVar[int]
    ENUM_VALUE_FIELD_NUMBER: _ClassVar[int]
    STRING_VALUE_FIELD_NUMBER: _ClassVar[int]
    OPERATOR_FIELD_NUMBER: _ClassVar[int]
    field: _field_pb2.FieldProto
    field_value_packed: _any_pb2.Any
    enum_value: int
    string_value: str
    operator: PositionFilterOperator
    def __init__(self, field: _Optional[_Union[_field_pb2.FieldProto, str]] = ..., field_value_packed: _Optional[_Union[_any_pb2.Any, _Mapping]] = ..., enum_value: _Optional[int] = ..., string_value: _Optional[str] = ..., operator: _Optional[_Union[PositionFilterOperator, str]] = ...) -> None: ...
