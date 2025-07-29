from google.protobuf.any_pb2 import Any
from datetime import datetime

from fintekkers.models.portfolio.portfolio_pb2 import PortfolioProto
from fintekkers.models.position.field_pb2 import FieldProto
from fintekkers.models.position.position_filter_pb2 import PositionFilterProto
from fintekkers.models.position.position_util_pb2 import FieldMapEntry
from fintekkers.models.util.local_timestamp_pb2 import LocalTimestampProto

from fintekkers.requests.portfolio.create_portfolio_request_pb2 import (
    CreatePortfolioRequestProto,
)
from fintekkers.requests.portfolio.query_portfolio_request_pb2 import (
    QueryPortfolioRequestProto,
)

from fintekkers.wrappers.models.portfolio import Portfolio
from fintekkers.wrappers.models.util.serialization import ProtoSerializationUtil


class CreatePortfolioRequest:
    @staticmethod
    def create_portfolio_request_from_name(
        portfolio_name: str,
    ):
        return CreatePortfolioRequestProto(
            create_portfolio_input=Portfolio.create_portfolio(portfolio_name).proto
        )

    @staticmethod
    def create_portfolio_request_from_proto(
        portfolio: PortfolioProto,
    ):
        return CreatePortfolioRequestProto(
            create_portfolio_input=portfolio
        )


class QueryPortfolioRequest:
    @staticmethod
    def create_query_request(fields: dict):
        """
        Returns a query request from a dict of field/values

                Parameters:
                        fields (dict): A dictionary of fields with values

                Returns:
                        request (CreateTransactionRequest): A request wrapper, with the fields attached. It assumes that all filters are an equals operation
        """

        filters = []

        # TODO: This code is duplicated in transaction.py
        for field in fields:
            field: FieldProto

            field_value = fields[field]
            entry = None

            if field_value.__class__ == str:
                entry = FieldMapEntry(field=field, string_value=field_value)
            else:
                packed_value = Any()
                packed_value.Pack(msg=field_value)

                entry = FieldMapEntry(field=field, field_value_packed=packed_value)

            filters.append(entry)

        as_of_proto: LocalTimestampProto = ProtoSerializationUtil.serialize(
            datetime.now()
        )

        query_request: QueryPortfolioRequestProto = QueryPortfolioRequestProto(
            search_portfolio_input=PositionFilterProto(filters=filters),
            as_of=as_of_proto,
        )

        return QueryPortfolioRequest(query_request)

    def __init__(self, proto: QueryPortfolioRequestProto):
        self.proto = proto
