from datetime import date, datetime
from typing import Generator
from uuid import UUID
import grpc
from grpc import RpcError
from fintekkers.models.position.field_pb2 import FieldProto
from fintekkers.models.price.price_pb2 import PriceProto
from fintekkers.models.security.identifier.identifier_pb2 import IdentifierProto
from fintekkers.models.security.identifier.identifier_type_pb2 import IdentifierTypeProto
from fintekkers.models.util.uuid_pb2 import UUIDProto
from fintekkers.requests.price.query_price_request_pb2 import (
    PriceFrequencyProto, PriceHorizonProto, QueryPriceRequestProto,
    PRICE_FREQUENCY_MINUTE, PRICE_FREQUENCY_HOURLY, PRICE_FREQUENCY_DAILY, 
    PRICE_FREQUENCY_WEEKLY, PRICE_HORIZON_1_DAY, PRICE_HORIZON_5_DAYS,
    PRICE_HORIZON_1_WEEK, PRICE_HORIZON_1_MONTH, PRICE_HORIZON_6_MONTHS,
    PRICE_HORIZON_1_YEAR, PRICE_HORIZON_5_YEAR, PRICE_HORIZON_MAX,
    PRICE_HORIZON_YEAR_TO_DATE
)
from fintekkers.requests.price.query_price_response_pb2 import QueryPriceResponseProto

from fintekkers.wrappers.models.price import Price
from fintekkers.wrappers.models.util.serialization import ProtoSerializationUtil
from fintekkers.wrappers.requests.price import CreatePriceRequest, QueryPriceRequest
from fintekkers.wrappers.requests.security import QuerySecurityRequest

from fintekkers.wrappers.services.util.Environment import EnvConfig, ServiceType
from fintekkers.wrappers.services.security import SecurityService

from fintekkers.services.price_service.price_service_pb2_grpc import PriceStub

class PriceService:
    def __init__(self):
        #By default will access the broker. 
        print("PriceService connecting to: " + EnvConfig.api_url())
        self.stub = PriceStub(EnvConfig.get_channel())

    def get_price(identifer:str, identifier_type: IdentifierTypeProto):
        return #the latest price

    def get_price(identifer:str, identifier_type: IdentifierTypeProto, asof:datetime):
        return #the latest price for the date

    def get_price(identifer:str, identifier_type: IdentifierTypeProto, asof:date):
        return #the latest price for the date
    

    def _get_frequency_for_horizon(self, horizon: PriceHorizonProto) -> PriceFrequencyProto:
        """
        Maps a price horizon to an appropriate frequency for data retrieval.
        
        Args:
            horizon: The time horizon for the price data
            
        Returns:
            The appropriate frequency for the given horizon
        """
        if horizon == PRICE_HORIZON_1_DAY:
            return PRICE_FREQUENCY_MINUTE
        elif horizon == PRICE_HORIZON_5_DAYS:
            return PRICE_FREQUENCY_HOURLY
        elif horizon == PRICE_HORIZON_1_WEEK:
            return PRICE_FREQUENCY_HOURLY
        elif horizon == PRICE_HORIZON_1_MONTH:
            return PRICE_FREQUENCY_DAILY
        elif horizon == PRICE_HORIZON_6_MONTHS:
            return PRICE_FREQUENCY_DAILY
        elif horizon == PRICE_HORIZON_1_YEAR:
            return PRICE_FREQUENCY_DAILY
        elif horizon == PRICE_HORIZON_5_YEAR:
            return PRICE_FREQUENCY_WEEKLY
        elif horizon == PRICE_HORIZON_MAX:
            return PRICE_FREQUENCY_WEEKLY
        elif horizon == PRICE_HORIZON_YEAR_TO_DATE:
            return PRICE_FREQUENCY_DAILY
        else:
            # Default to daily frequency for unspecified or unknown horizons
            return PRICE_FREQUENCY_DAILY

    def get_prices(self, identifer:str, identifier_type: IdentifierTypeProto, horizon: PriceHorizonProto) -> Generator[Price, None, None]:
        # Map horizon to appropriate frequency
        frequency: PriceFrequencyProto = self._get_frequency_for_horizon(horizon)

        # Get security uuid from identifier and identifier type via the security service
        security_uuid: UUID = SecurityService().get_security_uuid_by_identifier(identifer, identifier_type)

        # Create price query request using the security UUID, frequency, and horizon
        # uuid_proto = UUIDProto(raw_uuid=security_uuid.bytes)
        request = QueryPriceRequest.create_query_request(
            fields={
                FieldProto.SECURITY_ID: security_uuid
            },
            frequency=frequency,
            horizon=horizon
        )

        # Yield each price as it comes in from the search
        for price in self.search(request):
            yield price

    def search(self, request: QueryPriceRequest) -> Generator[Price, None, None]:
        responses = self.stub.Search(request=request.proto)

        try:
            while not responses._is_complete():
                response: QueryPriceResponseProto = responses.next()

                for price_proto in response.price_response:
                    yield Price(price_proto)
        except RpcError as e:
            if e.code() == grpc.StatusCode.CANCELLED:
                print(f"Network call cancelled, likely due to a service error trying to contact {EnvConfig.api_url()} ({e.details()})")
            else:
                print(f"Service unavailable trying to contact {EnvConfig.api_url()} ({e.details()})")
            raise e

        # This will send the cancel message to the server to kill the connection
        try:
            responses.cancel()
        except Exception as e:
            print(f"Error cancelling response stream: {e}")

    def create_or_update(self, request: CreatePriceRequest):
        try:
            return self.stub.CreateOrUpdate(request.proto)
        except RpcError as e:
            if e.code() == grpc.StatusCode.CANCELLED:
                print(f"Network call cancelled, likely due to a service error trying to contact {EnvConfig.api_url()} ({e.details()})")
            else:
                print(f"Service unavailable trying to contact {EnvConfig.api_url()} ({e.details()})")
            raise e
        
    def get_price_by_uuid(self,uuid: UUID) -> Price:
        """
        Parameters:
            A UUID

        Returns:
            request (Price): Returns the Price proto for the UUID, or None if doesn't exist
        """
        uuid_proto = UUIDProto(raw_uuid=uuid.bytes)

        # request: QueryPriceRequest = QueryPriceRequest.create_query_request(
        #     {
        #         FieldProto.ID: uuid_proto,
        #     },
        #     frequency=None,
        #     start_date=None,
        #     end_date=None
        # )

        request:QueryPriceRequestProto = QueryPriceRequestProto(
            uuIds=[uuid_proto]
        )

        try:
            prices = self.stub.GetByIds(request).price_response

            for price in prices:
                return Price(price)
        except RpcError as e:
            if e.code() == grpc.StatusCode.CANCELLED:
                print(f"Network call cancelled, likely due to a service error trying to contact {EnvConfig.api_url()} ({e.details()})")
            else:
                print(f"Service unavailable trying to contact {EnvConfig.api_url()} ({e.details()})")
            raise e
        
    def list_ids(self) -> list[UUID]:
        request: QueryPriceRequest = QueryPriceRequest.create_query_request(
            fields={},
            frequency=None,
            start_date=None,
            end_date=None
        )

        try:
            response: QueryPriceResponseProto = self.stub.ListIds(request.proto)

            ids: list[UUID] = []

            for price_proto in response.price_response:
                price_proto: PriceProto
                price_id = price_proto.uuid
                uuid: UUID = ProtoSerializationUtil.deserialize(price_id).as_uuid()
                ids.append(uuid)

            return ids
        except RpcError as e:
            if e.code() == grpc.StatusCode.CANCELLED:
                print(f"Network call cancelled, likely due to a service error trying to contact {EnvConfig.api_url()} ({e.details()})")
            else:
                print(f"Service unavailable trying to contact {EnvConfig.api_url()} ({e.details()})")
            raise e
