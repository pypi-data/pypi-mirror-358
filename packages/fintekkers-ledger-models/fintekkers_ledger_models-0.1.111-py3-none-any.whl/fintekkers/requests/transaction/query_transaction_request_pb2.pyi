from fintekkers.models.util import uuid_pb2 as _uuid_pb2
from fintekkers.models.util import local_timestamp_pb2 as _local_timestamp_pb2
from fintekkers.models.position import position_filter_pb2 as _position_filter_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class QueryTransactionRequestProto(_message.Message):
    __slots__ = ("object_class", "version", "uuIds", "search_transaction_input", "as_of", "limit")
    OBJECT_CLASS_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    UUIDS_FIELD_NUMBER: _ClassVar[int]
    SEARCH_TRANSACTION_INPUT_FIELD_NUMBER: _ClassVar[int]
    AS_OF_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    object_class: str
    version: str
    uuIds: _containers.RepeatedCompositeFieldContainer[_uuid_pb2.UUIDProto]
    search_transaction_input: _position_filter_pb2.PositionFilterProto
    as_of: _local_timestamp_pb2.LocalTimestampProto
    limit: int
    def __init__(self, object_class: _Optional[str] = ..., version: _Optional[str] = ..., uuIds: _Optional[_Iterable[_Union[_uuid_pb2.UUIDProto, _Mapping]]] = ..., search_transaction_input: _Optional[_Union[_position_filter_pb2.PositionFilterProto, _Mapping]] = ..., as_of: _Optional[_Union[_local_timestamp_pb2.LocalTimestampProto, _Mapping]] = ..., limit: _Optional[int] = ...) -> None: ...
