from typing import Generator
from uuid import UUID
from fintekkers.models.position.field_pb2 import FieldProto
from fintekkers.models.util.uuid_pb2 import UUIDProto
from fintekkers.models.position.position_util_pb2 import FieldMapEntry
from fintekkers.models.security.identifier.identifier_pb2 import IdentifierProto
from fintekkers.models.security.identifier.identifier_type_pb2 import IdentifierTypeProto
from fintekkers.requests.security.query_security_response_pb2 import (
    QuerySecurityResponseProto,
)
from fintekkers.services.security_service.security_service_pb2_grpc import SecurityStub
from fintekkers.models.position.position_pb2 import PositionProto

from fintekkers.wrappers.models.position import Position
from fintekkers.wrappers.models.security.security import Security
from fintekkers.wrappers.requests.security import (
    QuerySecurityRequest,
    CreateSecurityRequest,
)
from fintekkers.wrappers.services.util.Environment import EnvConfig

from fintekkers.requests.security.get_fields_response_pb2 import GetFieldsResponseProto
from fintekkers.requests.security.get_field_values_response_pb2 import GetFieldValuesResponseProto
from google.protobuf.empty_pb2 import Empty
from google.protobuf.any_pb2 import Any
from fintekkers.requests.security.get_field_values_request_pb2 import GetFieldValuesRequestProto
from fintekkers.wrappers.models.util.serialization import ProtoSerializationUtil

class SecurityService:
    def __init__(self):
        print("SecurityService connecting to: " + EnvConfig.api_url())
        self.stub = SecurityStub(EnvConfig.get_channel())

    def search(self, request: QuerySecurityRequest) -> Generator[Security, None, None]:
        responses = self.stub.Search(request=request.proto)

        try:
            while not responses._is_complete():
                response: QuerySecurityResponseProto = responses.next()

                for security_proto in response.security_response:
                    yield Security(security_proto)
        except StopIteration:
            pass
        except Exception as e:
            print(e)

        # This will send the cancel message to the server to kill the connection
        responses.cancel()

    def create_or_update(self, request: CreateSecurityRequest):
        return self.stub.CreateOrUpdate(request.proto)

    def get_security_by_uuid(self, uuid: UUID) -> Security:
        """
        Parameters:
            A UUID

        Returns:
            request (SecurityProto): Returns the Security proto for the UUID, or None if doesn't exist
        """
        uuid_proto = UUIDProto(raw_uuid=uuid.bytes)

        request: QuerySecurityRequest = QuerySecurityRequest.create_query_request(
            {
                FieldProto.ID: uuid_proto,
            }
        )

        securities = self.search(request)

        for security in securities:
            return security

    def get_security_uuid_by_identifier(self, identifier: str, identifier_type: IdentifierTypeProto) -> UUID:
        """
        Gets the security UUID from an identifier and identifier type.
        
        Args:
            identifier: The identifier value (e.g., "912796Y29")
            identifier_type: The type of identifier (e.g., CUSIP)
            
        Returns:
            The UUID of the security
            
        Raises:
            ValueError: If no security is found with the given identifier
        """
        # Create identifier proto
        identifier_proto = IdentifierProto(
            identifier_type=identifier_type,
            identifier_value=identifier
        )
        
        # Create security query request
        security_query_request = QuerySecurityRequest.create_query_request({
            FieldProto.IDENTIFIER: identifier_proto
        })
        
        # Search for the security
        for security in self.search(security_query_request):
            return security.get_id()  # Return the first security found
        
        # If no security found, raise an error
        raise ValueError(f"Security not found for identifier: {identifier} of type: {identifier_type}")

    def get_fields(self) -> list[FieldProto]:
        response:GetFieldsResponseProto = self.stub.GetFields(Empty())
        return response.fields

    def get_field_values(self, field:FieldProto) -> list[object]:
        request = GetFieldValuesRequestProto(field=field)
        response:GetFieldValuesResponseProto = self.stub.GetFieldValues(request)

        values = []
        for value in response.values:
            value:Any
            
            a: FieldMapEntry = FieldMapEntry(field=field, field_value_packed=value)

            ##TODO: This is a hack to get the field value. We need to find a better way to do this. 
            # Instead we should extract the logic relating to FieldMapEntry from Position
            # to make it reusable without having to create a Position object.
            position = Position(positionProto=PositionProto(fields=[a]))
            field_value = position.get_field(a)
            values.append(field_value)

        return values
