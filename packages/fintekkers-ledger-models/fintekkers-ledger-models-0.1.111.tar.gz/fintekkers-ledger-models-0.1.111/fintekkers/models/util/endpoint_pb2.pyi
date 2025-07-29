from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class Endpoint(_message.Message):
    __slots__ = ("ip", "port", "fully_qualified_url")
    IP_FIELD_NUMBER: _ClassVar[int]
    PORT_FIELD_NUMBER: _ClassVar[int]
    FULLY_QUALIFIED_URL_FIELD_NUMBER: _ClassVar[int]
    ip: str
    port: int
    fully_qualified_url: str
    def __init__(self, ip: _Optional[str] = ..., port: _Optional[int] = ..., fully_qualified_url: _Optional[str] = ...) -> None: ...
