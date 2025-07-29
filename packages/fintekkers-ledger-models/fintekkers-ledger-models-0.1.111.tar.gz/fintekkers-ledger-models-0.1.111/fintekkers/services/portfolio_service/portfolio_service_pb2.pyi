from fintekkers.requests.portfolio import create_portfolio_request_pb2 as _create_portfolio_request_pb2
from fintekkers.requests.portfolio import create_portfolio_response_pb2 as _create_portfolio_response_pb2
from fintekkers.requests.portfolio import query_portfolio_request_pb2 as _query_portfolio_request_pb2
from fintekkers.requests.portfolio import query_portfolio_response_pb2 as _query_portfolio_response_pb2
from fintekkers.requests.util.errors import summary_pb2 as _summary_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import service as _service
from typing import ClassVar as _ClassVar

DESCRIPTOR: _descriptor.FileDescriptor

class Portfolio(_service.service): ...

class Portfolio_Stub(Portfolio): ...
