from fintekkers.models.transaction import transaction_pb2 as _transaction_pb2
from fintekkers.requests.transaction import create_transaction_request_pb2 as _create_transaction_request_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CreateTransactionResponseProto(_message.Message):
    __slots__ = ("object_class", "version", "create_transaction_request", "transaction_response")
    OBJECT_CLASS_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    CREATE_TRANSACTION_REQUEST_FIELD_NUMBER: _ClassVar[int]
    TRANSACTION_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    object_class: str
    version: str
    create_transaction_request: _create_transaction_request_pb2.CreateTransactionRequestProto
    transaction_response: _transaction_pb2.TransactionProto
    def __init__(self, object_class: _Optional[str] = ..., version: _Optional[str] = ..., create_transaction_request: _Optional[_Union[_create_transaction_request_pb2.CreateTransactionRequestProto, _Mapping]] = ..., transaction_response: _Optional[_Union[_transaction_pb2.TransactionProto, _Mapping]] = ...) -> None: ...
