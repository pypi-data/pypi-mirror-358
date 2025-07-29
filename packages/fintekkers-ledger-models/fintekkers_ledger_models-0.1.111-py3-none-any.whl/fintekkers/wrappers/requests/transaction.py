from datetime import date
from google.protobuf.any_pb2 import Any

from fintekkers.models.portfolio.portfolio_pb2 import PortfolioProto
from fintekkers.models.position.field_pb2 import FieldProto
from fintekkers.models.position.position_filter_pb2 import PositionFilterProto
from fintekkers.models.position.position_status_pb2 import PositionStatusProto
from fintekkers.models.position.position_util_pb2 import FieldMapEntry
from fintekkers.models.security.security_pb2 import SecurityProto
from fintekkers.models.transaction.transaction_type_pb2 import TransactionTypeProto
from fintekkers.models.util.local_timestamp_pb2 import LocalTimestampProto

from fintekkers.requests.transaction.create_transaction_request_pb2 import CreateTransactionRequestProto
from fintekkers.requests.transaction.query_transaction_request_pb2 import QueryTransactionRequestProto

from fintekkers.wrappers.models.transaction import Transaction
from fintekkers.wrappers.models.util.serialization import ProtoSerializationUtil

from datetime import datetime

class CreateTransactionRequest():
    @staticmethod
    def create_transaction_request(
        security:SecurityProto=None, portfolio:PortfolioProto=None, \
        trade_date:date=date.today(), settlement_date:date=date.today(), \
        position_status:PositionStatusProto=PositionStatusProto.INTENDED, \
        transaction_type:TransactionTypeProto=TransactionTypeProto.BUY, \
        price:float=-100.00, quantity=100, as_of=datetime.now()
    ):
        '''
            Creates a request to create a transaction

                Parameters:
                        security (SecurityProto): A security proto, will be none if not provided (which would likely fail the creation request)
                        trade_date (date): The trade date, a.k.a the spot date
                        settlement_date (date): Settlement date of the trade
                        position_status (PositionStatusProto) The position status of the transaction, will default to INTENDED
                        transaction_type (TransactionTypeProto): The type of transaction, will default to BUY
                        price (float): Will default to 100 if not provided

                Returns:
                        request (CreateTransactionRequest): A request wrapper, with the fields attached. It assumes that all filters are an equals operation
        '''
        transaction:Transaction = Transaction.create_from(security=security, portfolio=portfolio, trade_date=trade_date, \
                                settlement_date=settlement_date, position_status=position_status, \
                                    transaction_type=transaction_type, price=price, quantity=quantity, as_of=as_of)
        
        proto:CreateTransactionRequestProto = CreateTransactionRequestProto(
            create_transaction_input=transaction.proto
        )
        return CreateTransactionRequest(proto=proto)
    
    def __init__(self, proto:CreateTransactionRequestProto):
        self.proto = proto

class QueryTransactionRequest():
    @staticmethod
    def create_query_request(fields:dict):
        '''
        Returns a query request from a dict of field/values

                Parameters:
                        fields (dict): A dictionary of fields with values

                Returns:
                        request (CreateTransactionRequest): A request wrapper, with the fields attached. It assumes that all filters are an equals operation
        '''

        filters = []

        for field in fields:
            field:FieldProto

            field_value = fields[field]            

            packed_value:Any = Any()
            packed_value.Pack(msg=field_value)

            entry = FieldMapEntry(
                field=field, field_value_packed=packed_value
            )

            filters.append(entry)
        
        as_of_proto:LocalTimestampProto = ProtoSerializationUtil.serialize(datetime.now())

        query_request:QueryTransactionRequestProto = QueryTransactionRequestProto(
            search_transaction_input=PositionFilterProto(
                filters=filters
            ),
            as_of=as_of_proto
        )

        return query_request
    
    def __init__(self, proto:QueryTransactionRequestProto):
        self.proto = proto