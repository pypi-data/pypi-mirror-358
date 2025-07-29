from fintekkers.models.position import position_util_pb2 as _position_util_pb2
from fintekkers.requests.valuation import valuation_request_pb2 as _valuation_request_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ValuationResponseProto(_message.Message):
    __slots__ = ("object_class", "version", "valuation_request", "measure_results")
    OBJECT_CLASS_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    VALUATION_REQUEST_FIELD_NUMBER: _ClassVar[int]
    MEASURE_RESULTS_FIELD_NUMBER: _ClassVar[int]
    object_class: str
    version: str
    valuation_request: _valuation_request_pb2.ValuationRequestProto
    measure_results: _containers.RepeatedCompositeFieldContainer[_position_util_pb2.MeasureMapEntry]
    def __init__(self, object_class: _Optional[str] = ..., version: _Optional[str] = ..., valuation_request: _Optional[_Union[_valuation_request_pb2.ValuationRequestProto, _Mapping]] = ..., measure_results: _Optional[_Iterable[_Union[_position_util_pb2.MeasureMapEntry, _Mapping]]] = ...) -> None: ...
