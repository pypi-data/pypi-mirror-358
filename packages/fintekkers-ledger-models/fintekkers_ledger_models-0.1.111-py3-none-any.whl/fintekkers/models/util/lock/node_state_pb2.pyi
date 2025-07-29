from fintekkers.models.util import local_timestamp_pb2 as _local_timestamp_pb2
from fintekkers.models.util import endpoint_pb2 as _endpoint_pb2
from fintekkers.models.util.lock import node_partition_pb2 as _node_partition_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class NodeState(_message.Message):
    __slots__ = ("object_class", "version", "partition", "end_point", "last_seen", "is_expired")
    OBJECT_CLASS_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    PARTITION_FIELD_NUMBER: _ClassVar[int]
    END_POINT_FIELD_NUMBER: _ClassVar[int]
    LAST_SEEN_FIELD_NUMBER: _ClassVar[int]
    IS_EXPIRED_FIELD_NUMBER: _ClassVar[int]
    object_class: str
    version: str
    partition: _node_partition_pb2.NodePartition
    end_point: _endpoint_pb2.Endpoint
    last_seen: _local_timestamp_pb2.LocalTimestampProto
    is_expired: bool
    def __init__(self, object_class: _Optional[str] = ..., version: _Optional[str] = ..., partition: _Optional[_Union[_node_partition_pb2.NodePartition, _Mapping]] = ..., end_point: _Optional[_Union[_endpoint_pb2.Endpoint, _Mapping]] = ..., last_seen: _Optional[_Union[_local_timestamp_pb2.LocalTimestampProto, _Mapping]] = ..., is_expired: bool = ...) -> None: ...
