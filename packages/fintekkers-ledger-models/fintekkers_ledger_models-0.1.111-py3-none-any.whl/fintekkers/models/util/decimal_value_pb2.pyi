from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class DecimalValueProto(_message.Message):
    __slots__ = ("arbitrary_precision_value",)
    ARBITRARY_PRECISION_VALUE_FIELD_NUMBER: _ClassVar[int]
    arbitrary_precision_value: str
    def __init__(self, arbitrary_precision_value: _Optional[str] = ...) -> None: ...
