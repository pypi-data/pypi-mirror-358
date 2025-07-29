from typing import Generator

from google.protobuf.any_pb2 import Any
from google.protobuf import wrappers_pb2 as wrappers

from datetime import datetime

from fintekkers.models.portfolio.portfolio_pb2 import PortfolioProto
from fintekkers.models.position.position_filter_pb2 import PositionFilterProto
from fintekkers.models.position.position_util_pb2 import FieldMapEntry
from fintekkers.models.position import field_pb2
from fintekkers.models.util.local_timestamp_pb2 import LocalTimestampProto
from fintekkers.requests.portfolio.create_portfolio_request_pb2 import (
    CreatePortfolioRequestProto,
)
from fintekkers.requests.portfolio.create_portfolio_response_pb2 import (
    CreatePortfolioResponseProto,
)

from fintekkers.requests.portfolio.query_portfolio_request_pb2 import (
    QueryPortfolioRequestProto,
)
from fintekkers.requests.portfolio.query_portfolio_response_pb2 import (
    QueryPortfolioResponseProto,
)

from fintekkers.services.portfolio_service.portfolio_service_pb2_grpc import (
    PortfolioStub,
)

from fintekkers.wrappers.models.portfolio import Portfolio
from fintekkers.wrappers.models.util.serialization import ProtoSerializationUtil
from fintekkers.wrappers.requests.portfolio import (
    CreatePortfolioRequest,
    QueryPortfolioRequest,
)
from fintekkers.wrappers.services.util.Environment import EnvConfig


class PortfolioService:
    def __init__(self):
        print("PortfolioService connecting to: " + EnvConfig.api_url())
        self.stub = PortfolioStub(EnvConfig.get_channel())

    def search(
        self, request: QueryPortfolioRequest
    ) -> Generator[Portfolio, None, None]:
        responses = self.stub.Search(request=request.proto)

        try:
            while not responses._is_complete():
                response: QueryPortfolioResponseProto = responses.next()

                for portfolio_proto in response.portfolio_response:
                    yield Portfolio(portfolio_proto)
        except StopIteration:
            pass
        except Exception as e:
            print(e)

        # This will terminate the request but leave the TCP connection open
        # responses

        self.stub = PortfolioStub(EnvConfig.get_channel())

    def create_or_update(
        self, request: CreatePortfolioRequestProto
    ) -> Generator[Portfolio, None, None]:
        self.stub = PortfolioStub(EnvConfig.get_channel())
        return self.stub.CreateOrUpdate(request)

    def create_portfolio_by_name(self, portfolio_name: str) -> Portfolio:
        """
        Creates a new portfolio with the given portfolio name. Uniqueness
        is defined by the UUID so if you call this multiple times with
        the same value you will have multiple portfolios with the same
        name but different UUIDs.
        """
        create_portfolio_request: CreatePortfolioRequestProto = (
            CreatePortfolioRequest.create_portfolio_request_from_name(portfolio_name)
        )

        responses = self.create_or_update(create_portfolio_request)

        if len(responses.portfolio_response) > 0:
            for portfolio in responses.portfolio_response:
                return Portfolio(portfolio)

        else:
            print("Could not create portfolio. You should call the validate API to check its a valid request")
            return None

    def get_or_create_portfolio_by_name(self, portfolio_name: str) -> Portfolio:
        """
        Returns a single portfolio if it exists, and if it doesn't exist then it is
        created. This does not guarantee that there is only one portfolio with that
        name in the system, but is a helper function that assumes that is the case.
        """
        def wrap_string_to_any(my_string: str):
            my_any = Any()
            my_any.Pack(wrappers.StringValue(value=my_string))
            return my_any

        as_of_proto: LocalTimestampProto = ProtoSerializationUtil.serialize(
            datetime.now()
        )

        portfolio_query = QueryPortfolioRequestProto(
            search_portfolio_input=PositionFilterProto(
                filters=[
                    FieldMapEntry(
                        field=field_pb2.FieldProto.PORTFOLIO_NAME,
                        field_value_packed=wrap_string_to_any(portfolio_name),
                    )
                ]
            ),
            as_of=as_of_proto,
        )

        responses = self.search(QueryPortfolioRequest(portfolio_query))
        portfolios: list[Portfolio] = []

        for portfolio in responses:
            portfolio:PortfolioProto
            portfolios.append(Portfolio(portfolio))

        number_found = len(portfolios)

        if number_found == 0:
            return self.create_portfolio_by_name(portfolio_name=portfolio_name)
        else:
            return portfolios[0]
