from fintekkers.models.security.identifier.identifier_pb2 import IdentifierProto
from fintekkers.models.security.security_pb2 import SecurityProto

from fintekkers.models.position.field_pb2 import *
from fintekkers.models.position.measure_pb2 import MeasureProto

from uuid import UUID
from datetime import datetime
from fintekkers.models.security.security_type_pb2 import SecurityTypeProto
from fintekkers.wrappers.models.security.security_identifier import Identifier

from fintekkers.wrappers.models.util.fintekkers_uuid import FintekkersUuid
from fintekkers.wrappers.models.util.serialization import ProtoSerializationUtil

class IFinancialModelObject:
    def get_field(field:FieldProto) -> object:
        pass

    def get_measure(measure:MeasureProto) -> object:
        pass

    def get_fields() -> set[FieldProto]:
        pass

    def get_measures() -> set[MeasureProto]:
        pass

    def get_as_of() -> datetime:
        pass

class RawDataModelObject:
    def __init__(self, id: UUID, as_of: datetime):
        self.id = id
        self.as_of = as_of

class Security():
    def __init__(self, proto:SecurityProto):
        self.proto:SecurityProto = proto

    def __str__(self) -> str:
        return f"ID[{str(self.get_id())}], {self.get_security_id()}[{self.proto.issuer_name}]"

    def get_fields(self) -> list[FieldProto]:
        return [
            ID, SECURITY_ID, AS_OF, ASSET_CLASS, IDENTIFIER
        ]

    def get_field(self, field:FieldProto) -> object:
        if field in (ID, SECURITY_ID):
            return self.get_id()
        elif field == AS_OF:
            return self.get_as_of()
        elif field == ASSET_CLASS:
            return self.get_asset_class()
        elif field == PRODUCT_CLASS:
            return self.get_product_class()
        elif field == PRODUCT_TYPE:
            return self.get_product_type()
        elif field == IDENTIFIER:
            return self.get_security_id()
        elif field in (TENOR, ADJUSTED_TENOR):
            return self.get_tenor()
        elif field == MATURITY_DATE:
            return self.get_maturity_date()
        elif field == ISSUE_DATE:
            return self.get_issue_date()
        else:
            raise ValueError(f"Field not mapped in Security wrapper: {FieldProto.DESCRIPTOR.values_by_number[field].name}")

    def get_id(self) -> UUID:
        uuid:FintekkersUuid = ProtoSerializationUtil.deserialize(self.proto.uuid)
        return uuid.uuid
    
    def get_as_of(self) -> datetime:
        as_of:datetime = ProtoSerializationUtil.deserialize(self.proto.as_of)
        return as_of
        
    def get_asset_class(self) -> str:
        return self.proto.asset_class
    
    def get_product_class(self) -> str:
        raise ValueError("Not implemented yet. See Java implementation for reference")
    
    def get_product_type(self) -> object:
        raise ValueError("Not implemented yet. See Java implementation for reference")
    
    def get_security_id(self) -> Identifier:
        id:IdentifierProto = self.proto.identifier
        return Identifier(id)
    
    def get_issue_date(self) -> datetime:
        return ProtoSerializationUtil.deserialize(self.proto.issue_date)

    def get_maturity_date(self) -> datetime:
        return ProtoSerializationUtil.deserialize(self.proto.maturity_date)
    
    def get_tenor(self) -> str:
        return ProtoSerializationUtil.deserialize(self.proto.tenor)

    def get_security_type(self) -> SecurityTypeProto:
        return self.proto.security_type

    def get_description(self) -> str:
        return self.proto.description

    def __str__(self):
        return f'ID[{str(self.get_security_id())}], {type(self).__name__}[{self.proto.issuer_name}]'

    def __eq__(self, other):
        if isinstance(other, Security):
            return self.get_id() == other.get_id()
        else:
            return False

    def __lt__(self, other):
        if isinstance(other, Security):
            return self.get_id() < other.get_id()
        else:
            return False

    def __hash__(self):
        return hash(self.get_id())
