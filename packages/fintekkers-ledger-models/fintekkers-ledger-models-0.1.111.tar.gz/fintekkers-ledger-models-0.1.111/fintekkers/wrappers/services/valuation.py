import grpc
from grpc import RpcError
from fintekkers.models.position.measure_pb2 import MeasureProto
from fintekkers.models.position.position_util_pb2 import MeasureMapEntry
from fintekkers.models.position.position_pb2 import PositionProto
from fintekkers.models.price.price_pb2 import PriceProto
from fintekkers.models.security.security_pb2 import SecurityProto
from fintekkers.requests.valuation.valuation_request_pb2 import ValuationRequestProto
from fintekkers.requests.valuation.valuation_response_pb2 import ValuationResponseProto
from fintekkers.requests.util.operation_pb2 import RequestOperationTypeProto, CREATE
from fintekkers.services.valuation_service.valuation_service_pb2_grpc import ValuationStub
from fintekkers.wrappers.models.position import Position
from fintekkers.wrappers.models.price import Price
from fintekkers.wrappers.models.security.security import Security
from fintekkers.wrappers.models.util.serialization import ProtoSerializationUtil
from fintekkers.wrappers.services.util.Environment import EnvConfig


class ValuationService:
    def __init__(self):
        print("ValuationService connecting to: " + EnvConfig.api_url())
        self.stub = ValuationStub(EnvConfig.get_channel())

    def run_valuation(self, 
                     security: Security = None, 
                     position: Position = None, 
                     price: Price = None,
                     measures: list[MeasureProto] = None) -> ValuationResponseProto:
        """
        Runs a valuation with the provided inputs.
        
        Args:
            security: The security to value (optional)
            position: The position to value (optional)
            price: The price to use for valuation (optional)
            measures: List of measures to calculate (optional)
            operation_type: The type of operation to perform (default: CREATE)
            
        Returns:
            ValuationResponseProto containing the valuation results
            
        Raises:
            RpcError: If the gRPC call fails
        """
        try:
            # Create the valuation request
            request = ValuationRequestProto(
                measures=measures or [],
                security_input=security.proto,
                position_input=position.positionProto,
                price_input=price.proto
            )
                
            # Run the valuation
            response = self.stub.RunValuation(request)
            return response
            
        except RpcError as e:
            if e.code() == grpc.StatusCode.CANCELLED:
                print(f"Network call cancelled, likely due to a service error trying to contact {EnvConfig.api_url()} ({e.details()})")
            else:
                print(f"Service unavailable trying to contact {EnvConfig.api_url()} ({e.details()})")
            raise e

    def get_measure_result(self, response: ValuationResponseProto, measure: MeasureProto) -> float:
        """
        Extracts a specific measure result from the valuation response.
        
        Args:
            response: The valuation response
            measure: The measure to extract
            
        Returns:
            The measure value as a float
            
        Raises:
            ValueError: If the measure is not found in the response
        """
        for measure_entry in response.measure_results:
            if measure_entry.measure == measure:
                return ProtoSerializationUtil.deserialize(measure_entry.measure_decimal_value)
        
        raise ValueError(f"Measure {measure} not found in valuation response") 