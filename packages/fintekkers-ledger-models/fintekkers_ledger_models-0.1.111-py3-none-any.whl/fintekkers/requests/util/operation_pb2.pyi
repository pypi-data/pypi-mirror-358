from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from typing import ClassVar as _ClassVar

DESCRIPTOR: _descriptor.FileDescriptor

class RequestOperationTypeProto(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UNKNOWN_OPERATION: _ClassVar[RequestOperationTypeProto]
    VALIDATE: _ClassVar[RequestOperationTypeProto]
    CREATE: _ClassVar[RequestOperationTypeProto]
    GET: _ClassVar[RequestOperationTypeProto]
    SEARCH: _ClassVar[RequestOperationTypeProto]
UNKNOWN_OPERATION: RequestOperationTypeProto
VALIDATE: RequestOperationTypeProto
CREATE: RequestOperationTypeProto
GET: RequestOperationTypeProto
SEARCH: RequestOperationTypeProto
