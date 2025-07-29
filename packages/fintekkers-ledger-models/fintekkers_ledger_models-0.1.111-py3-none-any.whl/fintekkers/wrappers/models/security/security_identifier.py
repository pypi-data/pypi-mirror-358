
from fintekkers.models.security.identifier.identifier_pb2 import IdentifierProto
from fintekkers.models.security.identifier.identifier_type_pb2 import IdentifierTypeProto

class Identifier():
    def __init__(self, identifier:IdentifierProto):
        self.proto = identifier

    def __str__(self):
        identifier_type_name = IdentifierTypeProto.DESCRIPTOR.values_by_number[self.proto.identifier_type].name
        return f"{identifier_type_name}:{self.proto.identifier_value}"
    
    def get_identifier_value(self) -> str:
        return self.proto.identifier_value
    
    def get_identifier_type(self) -> IdentifierTypeProto:
        return self.proto.identifier_type