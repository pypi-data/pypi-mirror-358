from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class API_Key(_message.Message):
    __slots__ = ("object_class", "version", "identity", "key")
    OBJECT_CLASS_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    IDENTITY_FIELD_NUMBER: _ClassVar[int]
    KEY_FIELD_NUMBER: _ClassVar[int]
    object_class: str
    version: str
    identity: str
    key: str
    def __init__(self, object_class: _Optional[str] = ..., version: _Optional[str] = ..., identity: _Optional[str] = ..., key: _Optional[str] = ...) -> None: ...
