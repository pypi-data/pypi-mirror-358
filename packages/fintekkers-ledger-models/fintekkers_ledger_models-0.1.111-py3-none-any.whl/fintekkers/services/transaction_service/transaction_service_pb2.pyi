from fintekkers.requests.transaction import create_transaction_request_pb2 as _create_transaction_request_pb2
from fintekkers.requests.transaction import create_transaction_response_pb2 as _create_transaction_response_pb2
from fintekkers.requests.transaction import query_transaction_request_pb2 as _query_transaction_request_pb2
from fintekkers.requests.transaction import query_transaction_response_pb2 as _query_transaction_response_pb2
from fintekkers.requests.util.errors import summary_pb2 as _summary_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import service as _service
from typing import ClassVar as _ClassVar

DESCRIPTOR: _descriptor.FileDescriptor

class Transaction(_service.service): ...

class Transaction_Stub(Transaction): ...
