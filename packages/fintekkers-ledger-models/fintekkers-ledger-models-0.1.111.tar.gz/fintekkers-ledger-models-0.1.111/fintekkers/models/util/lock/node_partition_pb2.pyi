from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class NodePartition(_message.Message):
    __slots__ = ("object_class", "version", "partition", "namespace")
    OBJECT_CLASS_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    PARTITION_FIELD_NUMBER: _ClassVar[int]
    NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    object_class: str
    version: str
    partition: int
    namespace: str
    def __init__(self, object_class: _Optional[str] = ..., version: _Optional[str] = ..., partition: _Optional[int] = ..., namespace: _Optional[str] = ...) -> None: ...
