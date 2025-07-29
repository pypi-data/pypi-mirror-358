from fintekkers.models.util import decimal_value_pb2 as _decimal_value_pb2
from fintekkers.models.util import local_date_pb2 as _local_date_pb2
from fintekkers.models.util import local_timestamp_pb2 as _local_timestamp_pb2
from fintekkers.models.util import uuid_pb2 as _uuid_pb2
from fintekkers.models.portfolio import portfolio_pb2 as _portfolio_pb2
from fintekkers.models.strategy import strategy_allocation_pb2 as _strategy_allocation_pb2
from fintekkers.models.security import security_pb2 as _security_pb2
from fintekkers.models.price import price_pb2 as _price_pb2
from fintekkers.models.position import position_status_pb2 as _position_status_pb2
from fintekkers.models.transaction import transaction_type_pb2 as _transaction_type_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TransactionProto(_message.Message):
    __slots__ = ("object_class", "version", "uuid", "as_of", "is_link", "valid_from", "valid_to", "portfolio", "security", "transaction_type", "quantity", "price", "trade_date", "settlement_date", "childTransactions", "position_status", "trade_name", "strategy_allocation", "is_cancelled")
    OBJECT_CLASS_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    UUID_FIELD_NUMBER: _ClassVar[int]
    AS_OF_FIELD_NUMBER: _ClassVar[int]
    IS_LINK_FIELD_NUMBER: _ClassVar[int]
    VALID_FROM_FIELD_NUMBER: _ClassVar[int]
    VALID_TO_FIELD_NUMBER: _ClassVar[int]
    PORTFOLIO_FIELD_NUMBER: _ClassVar[int]
    SECURITY_FIELD_NUMBER: _ClassVar[int]
    TRANSACTION_TYPE_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    PRICE_FIELD_NUMBER: _ClassVar[int]
    TRADE_DATE_FIELD_NUMBER: _ClassVar[int]
    SETTLEMENT_DATE_FIELD_NUMBER: _ClassVar[int]
    CHILDTRANSACTIONS_FIELD_NUMBER: _ClassVar[int]
    POSITION_STATUS_FIELD_NUMBER: _ClassVar[int]
    TRADE_NAME_FIELD_NUMBER: _ClassVar[int]
    STRATEGY_ALLOCATION_FIELD_NUMBER: _ClassVar[int]
    IS_CANCELLED_FIELD_NUMBER: _ClassVar[int]
    object_class: str
    version: str
    uuid: _uuid_pb2.UUIDProto
    as_of: _local_timestamp_pb2.LocalTimestampProto
    is_link: bool
    valid_from: _local_timestamp_pb2.LocalTimestampProto
    valid_to: _local_timestamp_pb2.LocalTimestampProto
    portfolio: _portfolio_pb2.PortfolioProto
    security: _security_pb2.SecurityProto
    transaction_type: _transaction_type_pb2.TransactionTypeProto
    quantity: _decimal_value_pb2.DecimalValueProto
    price: _price_pb2.PriceProto
    trade_date: _local_date_pb2.LocalDateProto
    settlement_date: _local_date_pb2.LocalDateProto
    childTransactions: _containers.RepeatedCompositeFieldContainer[TransactionProto]
    position_status: _position_status_pb2.PositionStatusProto
    trade_name: str
    strategy_allocation: _strategy_allocation_pb2.StrategyAllocationProto
    is_cancelled: bool
    def __init__(self, object_class: _Optional[str] = ..., version: _Optional[str] = ..., uuid: _Optional[_Union[_uuid_pb2.UUIDProto, _Mapping]] = ..., as_of: _Optional[_Union[_local_timestamp_pb2.LocalTimestampProto, _Mapping]] = ..., is_link: bool = ..., valid_from: _Optional[_Union[_local_timestamp_pb2.LocalTimestampProto, _Mapping]] = ..., valid_to: _Optional[_Union[_local_timestamp_pb2.LocalTimestampProto, _Mapping]] = ..., portfolio: _Optional[_Union[_portfolio_pb2.PortfolioProto, _Mapping]] = ..., security: _Optional[_Union[_security_pb2.SecurityProto, _Mapping]] = ..., transaction_type: _Optional[_Union[_transaction_type_pb2.TransactionTypeProto, str]] = ..., quantity: _Optional[_Union[_decimal_value_pb2.DecimalValueProto, _Mapping]] = ..., price: _Optional[_Union[_price_pb2.PriceProto, _Mapping]] = ..., trade_date: _Optional[_Union[_local_date_pb2.LocalDateProto, _Mapping]] = ..., settlement_date: _Optional[_Union[_local_date_pb2.LocalDateProto, _Mapping]] = ..., childTransactions: _Optional[_Iterable[_Union[TransactionProto, _Mapping]]] = ..., position_status: _Optional[_Union[_position_status_pb2.PositionStatusProto, str]] = ..., trade_name: _Optional[str] = ..., strategy_allocation: _Optional[_Union[_strategy_allocation_pb2.StrategyAllocationProto, _Mapping]] = ..., is_cancelled: bool = ...) -> None: ...
