from fintekkers.models.position import field_pb2 as _field_pb2
from fintekkers.models.position import measure_pb2 as _measure_pb2
from fintekkers.models.position import position_pb2 as _position_pb2
from fintekkers.models.position import position_filter_pb2 as _position_filter_pb2
from fintekkers.models.util import local_timestamp_pb2 as _local_timestamp_pb2
from fintekkers.requests.util import operation_pb2 as _operation_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class QueryPositionRequestProto(_message.Message):
    __slots__ = ("object_class", "version", "operation_type", "position_type", "position_view", "fields", "measures", "filter_fields", "as_of")
    OBJECT_CLASS_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    OPERATION_TYPE_FIELD_NUMBER: _ClassVar[int]
    POSITION_TYPE_FIELD_NUMBER: _ClassVar[int]
    POSITION_VIEW_FIELD_NUMBER: _ClassVar[int]
    FIELDS_FIELD_NUMBER: _ClassVar[int]
    MEASURES_FIELD_NUMBER: _ClassVar[int]
    FILTER_FIELDS_FIELD_NUMBER: _ClassVar[int]
    AS_OF_FIELD_NUMBER: _ClassVar[int]
    object_class: str
    version: str
    operation_type: _operation_pb2.RequestOperationTypeProto
    position_type: _position_pb2.PositionTypeProto
    position_view: _position_pb2.PositionViewProto
    fields: _containers.RepeatedScalarFieldContainer[_field_pb2.FieldProto]
    measures: _containers.RepeatedScalarFieldContainer[_measure_pb2.MeasureProto]
    filter_fields: _position_filter_pb2.PositionFilterProto
    as_of: _local_timestamp_pb2.LocalTimestampProto
    def __init__(self, object_class: _Optional[str] = ..., version: _Optional[str] = ..., operation_type: _Optional[_Union[_operation_pb2.RequestOperationTypeProto, str]] = ..., position_type: _Optional[_Union[_position_pb2.PositionTypeProto, str]] = ..., position_view: _Optional[_Union[_position_pb2.PositionViewProto, str]] = ..., fields: _Optional[_Iterable[_Union[_field_pb2.FieldProto, str]]] = ..., measures: _Optional[_Iterable[_Union[_measure_pb2.MeasureProto, str]]] = ..., filter_fields: _Optional[_Union[_position_filter_pb2.PositionFilterProto, _Mapping]] = ..., as_of: _Optional[_Union[_local_timestamp_pb2.LocalTimestampProto, _Mapping]] = ...) -> None: ...
