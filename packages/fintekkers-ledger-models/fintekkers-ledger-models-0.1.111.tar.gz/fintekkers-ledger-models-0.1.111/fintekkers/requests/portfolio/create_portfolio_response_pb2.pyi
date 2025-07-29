from fintekkers.models.portfolio import portfolio_pb2 as _portfolio_pb2
from fintekkers.requests.portfolio import create_portfolio_request_pb2 as _create_portfolio_request_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CreatePortfolioResponseProto(_message.Message):
    __slots__ = ("object_class", "version", "create_portfolio_request", "portfolio_response")
    OBJECT_CLASS_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    CREATE_PORTFOLIO_REQUEST_FIELD_NUMBER: _ClassVar[int]
    PORTFOLIO_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    object_class: str
    version: str
    create_portfolio_request: _create_portfolio_request_pb2.CreatePortfolioRequestProto
    portfolio_response: _containers.RepeatedCompositeFieldContainer[_portfolio_pb2.PortfolioProto]
    def __init__(self, object_class: _Optional[str] = ..., version: _Optional[str] = ..., create_portfolio_request: _Optional[_Union[_create_portfolio_request_pb2.CreatePortfolioRequestProto, _Mapping]] = ..., portfolio_response: _Optional[_Iterable[_Union[_portfolio_pb2.PortfolioProto, _Mapping]]] = ...) -> None: ...
