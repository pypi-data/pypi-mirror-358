from fintekkers.models.util import uuid_pb2 as _uuid_pb2
from fintekkers.models.util import local_timestamp_pb2 as _local_timestamp_pb2
from fintekkers.models.position import position_filter_pb2 as _position_filter_pb2
from fintekkers.models.util import date_range_pb2 as _date_range_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class PriceFrequencyProto(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    PRICE_FREQUENCY_UNSPECIFIED: _ClassVar[PriceFrequencyProto]
    PRICE_FREQUENCY_WEEKLY: _ClassVar[PriceFrequencyProto]
    PRICE_FREQUENCY_DAILY: _ClassVar[PriceFrequencyProto]
    PRICE_FREQUENCY_HOURLY: _ClassVar[PriceFrequencyProto]
    PRICE_FREQUENCY_MINUTE: _ClassVar[PriceFrequencyProto]
    PRICE_FREQUENCY_EVERY_TICK: _ClassVar[PriceFrequencyProto]

class PriceHorizonProto(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    PRICE_HORIZON_UNSPECIFIED: _ClassVar[PriceHorizonProto]
    PRICE_HORIZON_1_DAY: _ClassVar[PriceHorizonProto]
    PRICE_HORIZON_5_DAYS: _ClassVar[PriceHorizonProto]
    PRICE_HORIZON_1_WEEK: _ClassVar[PriceHorizonProto]
    PRICE_HORIZON_1_MONTH: _ClassVar[PriceHorizonProto]
    PRICE_HORIZON_6_MONTHS: _ClassVar[PriceHorizonProto]
    PRICE_HORIZON_1_YEAR: _ClassVar[PriceHorizonProto]
    PRICE_HORIZON_5_YEAR: _ClassVar[PriceHorizonProto]
    PRICE_HORIZON_MAX: _ClassVar[PriceHorizonProto]
    PRICE_HORIZON_YEAR_TO_DATE: _ClassVar[PriceHorizonProto]
PRICE_FREQUENCY_UNSPECIFIED: PriceFrequencyProto
PRICE_FREQUENCY_WEEKLY: PriceFrequencyProto
PRICE_FREQUENCY_DAILY: PriceFrequencyProto
PRICE_FREQUENCY_HOURLY: PriceFrequencyProto
PRICE_FREQUENCY_MINUTE: PriceFrequencyProto
PRICE_FREQUENCY_EVERY_TICK: PriceFrequencyProto
PRICE_HORIZON_UNSPECIFIED: PriceHorizonProto
PRICE_HORIZON_1_DAY: PriceHorizonProto
PRICE_HORIZON_5_DAYS: PriceHorizonProto
PRICE_HORIZON_1_WEEK: PriceHorizonProto
PRICE_HORIZON_1_MONTH: PriceHorizonProto
PRICE_HORIZON_6_MONTHS: PriceHorizonProto
PRICE_HORIZON_1_YEAR: PriceHorizonProto
PRICE_HORIZON_5_YEAR: PriceHorizonProto
PRICE_HORIZON_MAX: PriceHorizonProto
PRICE_HORIZON_YEAR_TO_DATE: PriceHorizonProto

class QueryPriceRequestProto(_message.Message):
    __slots__ = ("object_class", "version", "uuIds", "search_price_input", "as_of", "frequency", "horizon", "date_range")
    OBJECT_CLASS_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    UUIDS_FIELD_NUMBER: _ClassVar[int]
    SEARCH_PRICE_INPUT_FIELD_NUMBER: _ClassVar[int]
    AS_OF_FIELD_NUMBER: _ClassVar[int]
    FREQUENCY_FIELD_NUMBER: _ClassVar[int]
    HORIZON_FIELD_NUMBER: _ClassVar[int]
    DATE_RANGE_FIELD_NUMBER: _ClassVar[int]
    object_class: str
    version: str
    uuIds: _containers.RepeatedCompositeFieldContainer[_uuid_pb2.UUIDProto]
    search_price_input: _position_filter_pb2.PositionFilterProto
    as_of: _local_timestamp_pb2.LocalTimestampProto
    frequency: PriceFrequencyProto
    horizon: PriceHorizonProto
    date_range: _date_range_pb2.DateRangeProto
    def __init__(self, object_class: _Optional[str] = ..., version: _Optional[str] = ..., uuIds: _Optional[_Iterable[_Union[_uuid_pb2.UUIDProto, _Mapping]]] = ..., search_price_input: _Optional[_Union[_position_filter_pb2.PositionFilterProto, _Mapping]] = ..., as_of: _Optional[_Union[_local_timestamp_pb2.LocalTimestampProto, _Mapping]] = ..., frequency: _Optional[_Union[PriceFrequencyProto, str]] = ..., horizon: _Optional[_Union[PriceHorizonProto, str]] = ..., date_range: _Optional[_Union[_date_range_pb2.DateRangeProto, _Mapping]] = ...) -> None: ...
