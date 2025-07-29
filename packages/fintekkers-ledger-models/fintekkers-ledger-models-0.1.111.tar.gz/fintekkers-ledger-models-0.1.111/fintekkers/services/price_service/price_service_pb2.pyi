from fintekkers.requests.price import query_price_request_pb2 as _query_price_request_pb2
from fintekkers.requests.price import query_price_response_pb2 as _query_price_response_pb2
from fintekkers.requests.price import create_price_request_pb2 as _create_price_request_pb2
from fintekkers.requests.price import create_price_response_pb2 as _create_price_response_pb2
from fintekkers.requests.util.errors import summary_pb2 as _summary_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import service as _service
from typing import ClassVar as _ClassVar

DESCRIPTOR: _descriptor.FileDescriptor

class Price(_service.service): ...

class Price_Stub(Price): ...
