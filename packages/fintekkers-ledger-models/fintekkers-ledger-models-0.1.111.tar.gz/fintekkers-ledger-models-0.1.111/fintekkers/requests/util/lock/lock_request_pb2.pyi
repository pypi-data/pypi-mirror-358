from fintekkers.models.util.lock import node_partition_pb2 as _node_partition_pb2
from fintekkers.models.util import endpoint_pb2 as _endpoint_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class LockRequestProto(_message.Message):
    __slots__ = ("object_class", "version", "node_partition", "endpoint")
    OBJECT_CLASS_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    NODE_PARTITION_FIELD_NUMBER: _ClassVar[int]
    ENDPOINT_FIELD_NUMBER: _ClassVar[int]
    object_class: str
    version: str
    node_partition: _node_partition_pb2.NodePartition
    endpoint: _endpoint_pb2.Endpoint
    def __init__(self, object_class: _Optional[str] = ..., version: _Optional[str] = ..., node_partition: _Optional[_Union[_node_partition_pb2.NodePartition, _Mapping]] = ..., endpoint: _Optional[_Union[_endpoint_pb2.Endpoint, _Mapping]] = ...) -> None: ...
