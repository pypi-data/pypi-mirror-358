from fintekkers.models.position.position_status_pb2 import *
from fintekkers.models.security.identifier.identifier_pb2 import IdentifierProto
from fintekkers.models.security.tenor_pb2 import TenorProto
from fintekkers.models.util.local_date_pb2 import LocalDateProto
from fintekkers.models.util.local_timestamp_pb2 import LocalTimestampProto
from fintekkers.models.util.uuid_pb2 import UUIDProto
from fintekkers.models.util.decimal_value_pb2 import DecimalValueProto
from fintekkers.wrappers.models.security.security_identifier import Identifier
from fintekkers.wrappers.models.security.tenor import Tenor

from fintekkers.wrappers.models.transaction import TransactionType
from fintekkers.wrappers.models.util.fintekkers_uuid import FintekkersUuid

from google.protobuf.timestamp_pb2 import Timestamp
from datetime import date, datetime
import time
from pytz import timezone

from fintekkers.models.transaction.transaction_type_pb2 import TransactionTypeProto
from uuid import UUID, uuid4

from google._upb._message import EnumValueDescriptor
from google.protobuf.wrappers_pb2 import StringValue
from google.protobuf.any_pb2 import Any
class ProtoEnum:
    def __init__(self, enum_descriptor: EnumValueDescriptor, enum_value: int):
        self.enum_value: int = enum_value
        self.get_enum_descriptor = enum_descriptor
        # Will be the proto
        self.enum = ProtoEnum.get_field_descriptor(enum_descriptor)

    @staticmethod
    def from_enum_name(enum_name: str, enum_value: int):
        return ProtoEnum(
            ProtoEnum.get_field_descriptor_from_name(enum_name), enum_value
        )

    @staticmethod
    def get_field_descriptor(enum_descriptor: str):
        return ProtoEnum.get_field_descriptor_from_name(enum_descriptor.name)

    @staticmethod
    def get_field_descriptor_from_name(enum_name: str):
        if enum_name == "TRANSACTION_TYPE":
            return TransactionTypeProto
        if enum_name == "POSITION_STATUS":
            return PositionStatusProto

        raise ValueError(f"Enum has not been mapped: {enum_name}")

    def get_enum_name(self) -> str:
        """
        The string name of the enum
        """
        return self.enum_descriptor.name

    def get_enum_value(self) -> int:
        """
        Returns the numer of the enum value. Eg. zero generally means unknown,
        and 1 would be the first value in that enum."""
        return self.enum_value

    def get_enum_value_name(self) -> str:
        """
        Returns the string name of the enum, e.g. if the value is zero then
        this will generally be "UNKNOWN".
        """
        return self.enum.DESCRIPTOR.values_by_number[self.enum_value].name

    def __str__(self) -> str:
        return self.get_enum_value_name()


class ProtoSerializationUtil:
    @staticmethod
    def serialize(obj):
        if isinstance(obj, UUID):
            return UUIDProto(raw_uuid=obj.bytes)
        if isinstance(obj, Tenor):
            obj:Tenor
            return obj.as_proto()
        if type(obj) is date:
            return LocalDateProto(year=obj.year, month=obj.month, day=obj.day)
        if isinstance(obj, datetime):
            seconds_in_float: float = time.mktime(obj.timetuple())
            timestamp = Timestamp(
                seconds=int(seconds_in_float), nanos=int(obj.microsecond / 1000)
            )

            time_zone = (
                obj.timetz().tzinfo.zone
                if obj.timetz().tzinfo is not None
                else "America/New_York"
            )
            return LocalTimestampProto(timestamp=timestamp, time_zone=time_zone)
        if isinstance(obj, Identifier) or isinstance(obj, TransactionType):
            return obj.proto
        if isinstance(obj, float) or isinstance(obj, int):
            return DecimalValueProto(arbitrary_precision_value=str(obj))
        
        if isinstance(obj, str):
            return StringValue(value=obj)

        raise ValueError(
            f"Could not serialize object of type {obj.__class__.__name__}. Value: {obj}"
        )

    @staticmethod
    def deserialize(obj):
        if isinstance(obj, Any):
            #unpack a string value
            return StringValue.FromString(obj.value).value
        if isinstance(obj, UUIDProto):
            return FintekkersUuid.from_bytes(raw_uuid=obj.raw_uuid)
        if isinstance(obj, LocalDateProto):
            return date(year=obj.year, month=obj.month, day=obj.day)
        if isinstance(obj, LocalTimestampProto):
            return datetime.fromtimestamp(
                obj.timestamp.seconds, timezone(obj.time_zone)
            )
        if isinstance(obj, TenorProto):
            return Tenor(obj.tenor_type, obj.term_value)
        if isinstance(obj, IdentifierProto):
            return Identifier(obj)
        if isinstance(obj, DecimalValueProto):
            obj: DecimalValueProto
            return float(obj.arbitrary_precision_value)
        if (
            hasattr(obj, "enum_name")
            and getattr(obj, "enum_name") == "TRANSACTION_TYPE"
        ):
            return TransactionType(obj.enum_value)

        raise ValueError(
            f"Could not deserialize object of type {obj.__class__.__name__}. Value: {obj}"
        )

