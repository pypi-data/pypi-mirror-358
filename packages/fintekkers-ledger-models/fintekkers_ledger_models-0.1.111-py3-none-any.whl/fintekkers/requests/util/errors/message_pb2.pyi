from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class Message(_message.Message):
    __slots__ = ("message_for_user", "message_for_developer")
    MESSAGE_FOR_USER_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FOR_DEVELOPER_FIELD_NUMBER: _ClassVar[int]
    message_for_user: str
    message_for_developer: str
    def __init__(self, message_for_user: _Optional[str] = ..., message_for_developer: _Optional[str] = ...) -> None: ...
