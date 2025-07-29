from fintekkers.models.transaction import transaction_pb2 as _transaction_pb2
from fintekkers.requests.transaction import query_transaction_request_pb2 as _query_transaction_request_pb2
from fintekkers.requests.util.errors import summary_pb2 as _summary_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class QueryTransactionResponseProto(_message.Message):
    __slots__ = ("object_class", "version", "create_transaction_request", "transaction_response", "errors_or_warnings")
    OBJECT_CLASS_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    CREATE_TRANSACTION_REQUEST_FIELD_NUMBER: _ClassVar[int]
    TRANSACTION_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    ERRORS_OR_WARNINGS_FIELD_NUMBER: _ClassVar[int]
    object_class: str
    version: str
    create_transaction_request: _query_transaction_request_pb2.QueryTransactionRequestProto
    transaction_response: _containers.RepeatedCompositeFieldContainer[_transaction_pb2.TransactionProto]
    errors_or_warnings: _summary_pb2.SummaryProto
    def __init__(self, object_class: _Optional[str] = ..., version: _Optional[str] = ..., create_transaction_request: _Optional[_Union[_query_transaction_request_pb2.QueryTransactionRequestProto, _Mapping]] = ..., transaction_response: _Optional[_Iterable[_Union[_transaction_pb2.TransactionProto, _Mapping]]] = ..., errors_or_warnings: _Optional[_Union[_summary_pb2.SummaryProto, _Mapping]] = ...) -> None: ...
