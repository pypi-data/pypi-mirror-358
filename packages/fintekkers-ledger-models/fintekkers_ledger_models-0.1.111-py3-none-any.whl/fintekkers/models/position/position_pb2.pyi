from fintekkers.models.position import position_util_pb2 as _position_util_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class PositionViewProto(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UNKNOWN_POSITION_VIEW: _ClassVar[PositionViewProto]
    DEFAULT_VIEW: _ClassVar[PositionViewProto]
    STRATEGY_VIEW: _ClassVar[PositionViewProto]

class PositionTypeProto(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UNKNOWN_POSITION_TYPE: _ClassVar[PositionTypeProto]
    TRANSACTION: _ClassVar[PositionTypeProto]
    TAX_LOT: _ClassVar[PositionTypeProto]
UNKNOWN_POSITION_VIEW: PositionViewProto
DEFAULT_VIEW: PositionViewProto
STRATEGY_VIEW: PositionViewProto
UNKNOWN_POSITION_TYPE: PositionTypeProto
TRANSACTION: PositionTypeProto
TAX_LOT: PositionTypeProto

class PositionProto(_message.Message):
    __slots__ = ("object_class", "version", "position_view", "position_type", "measures", "fields")
    OBJECT_CLASS_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    POSITION_VIEW_FIELD_NUMBER: _ClassVar[int]
    POSITION_TYPE_FIELD_NUMBER: _ClassVar[int]
    MEASURES_FIELD_NUMBER: _ClassVar[int]
    FIELDS_FIELD_NUMBER: _ClassVar[int]
    object_class: str
    version: str
    position_view: PositionViewProto
    position_type: PositionTypeProto
    measures: _containers.RepeatedCompositeFieldContainer[_position_util_pb2.MeasureMapEntry]
    fields: _containers.RepeatedCompositeFieldContainer[_position_util_pb2.FieldMapEntry]
    def __init__(self, object_class: _Optional[str] = ..., version: _Optional[str] = ..., position_view: _Optional[_Union[PositionViewProto, str]] = ..., position_type: _Optional[_Union[PositionTypeProto, str]] = ..., measures: _Optional[_Iterable[_Union[_position_util_pb2.MeasureMapEntry, _Mapping]]] = ..., fields: _Optional[_Iterable[_Union[_position_util_pb2.FieldMapEntry, _Mapping]]] = ...) -> None: ...
