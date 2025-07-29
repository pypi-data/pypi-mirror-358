from datetime import date, datetime
from uuid import uuid4
from google.protobuf.timestamp_pb2 import Timestamp

from fintekkers.models.transaction.transaction_pb2 import TransactionProto
from fintekkers.models.transaction.transaction_type_pb2 import TransactionTypeProto

from fintekkers.models.portfolio.portfolio_pb2 import PortfolioProto
from fintekkers.models.position.position_status_pb2 import PositionStatusProto

from fintekkers.models.price.price_pb2 import PriceProto
from fintekkers.models.security.security_pb2 import SecurityProto

from fintekkers.models.util.local_date_pb2 import LocalDateProto
from fintekkers.models.util.local_timestamp_pb2 import LocalTimestampProto
from fintekkers.models.util.uuid_pb2 import UUIDProto
from fintekkers.models.util.decimal_value_pb2 import DecimalValueProto
from fintekkers.wrappers.models.util.date_utils import get_date_from_proto

class Transaction():
    @staticmethod
    def create_from(
        security:SecurityProto=None, portfolio:PortfolioProto=None, \
        trade_date:date=date.today(), settlement_date:date=date.today(), \
        position_status:PositionStatusProto=PositionStatusProto.INTENDED, \
        transaction_type:TransactionTypeProto=TransactionTypeProto.BUY, \
        price:float=-100.00, quantity=100, 
        as_of:datetime=datetime.now()):
        
        as_of_proto = LocalTimestampProto(timestamp=Timestamp(seconds=int(get_date_from_proto(as_of).timestamp()), nanos=0), time_zone="America/New_York")

        return Transaction(proto=TransactionProto(
            as_of=as_of_proto,
            is_cancelled=False,
            is_link=False,
            object_class="Transaction",
            portfolio=portfolio,
            security=security,
            position_status=position_status,
            price=PriceProto(
                uuid=UUIDProto(raw_uuid=uuid4().bytes),
                as_of=as_of_proto,
                price=DecimalValueProto(arbitrary_precision_value=f"{price}"),
                security=security
            ),
            transaction_type=transaction_type,
            quantity=DecimalValueProto(arbitrary_precision_value=f"{quantity}"),
            trade_date=LocalDateProto(year=trade_date.year, month=trade_date.month, day=trade_date.day),
            settlement_date=LocalDateProto(year=settlement_date.year, month=settlement_date.month, day=settlement_date.day),
            uuid=UUIDProto(raw_uuid=uuid4().bytes),
            trade_name="No trade name",
            strategy_allocation=None
        ))

    def __init__(self, proto:TransactionProto):
        self.proto:TransactionProto = proto

class TransactionType():
    def __init__(self, proto: TransactionTypeProto):
        self.proto = proto

    def __str__(self) -> str:
        return TransactionTypeProto.Name(self.proto)
