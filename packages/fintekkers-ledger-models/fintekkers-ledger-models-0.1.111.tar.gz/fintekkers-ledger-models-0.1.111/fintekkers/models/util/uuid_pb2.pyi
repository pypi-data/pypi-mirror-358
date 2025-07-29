from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class UUIDProto(_message.Message):
    __slots__ = ("raw_uuid",)
    RAW_UUID_FIELD_NUMBER: _ClassVar[int]
    raw_uuid: bytes
    def __init__(self, raw_uuid: _Optional[bytes] = ...) -> None: ...
