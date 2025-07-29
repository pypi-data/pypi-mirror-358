from fintekkers.models.position.field_pb2 import FieldProto
from fintekkers.models.position.measure_pb2 import MeasureProto
from fintekkers.models.position.position_pb2 import PositionProto
from fintekkers.models.position.position_util_pb2 import FieldMapEntry, MeasureMapEntry

from fintekkers.models.portfolio.portfolio_pb2 import PortfolioProto
from fintekkers.models.security.security_pb2 import SecurityProto
from fintekkers.models.security.identifier.identifier_pb2 import IdentifierProto

from fintekkers.models.util.local_date_pb2 import LocalDateProto
from fintekkers.models.util.local_timestamp_pb2 import LocalTimestampProto
from fintekkers.models.util.uuid_pb2 import UUIDProto
from fintekkers.wrappers.models.portfolio import Portfolio

from fintekkers.wrappers.models.security.security import Security
from fintekkers.wrappers.models.util.serialization import (
    ProtoSerializationUtil,
    ProtoEnum,
)

from google.protobuf import wrappers_pb2 as wrappers
from google.protobuf.any_pb2 import Any

from decimal import Decimal
from io import StringIO

from fintekkers.models.security.tenor_pb2 import TenorProto
class Position:
    positionProto: PositionProto

    def __init__(self, positionProto: PositionProto) -> None:
        self.positionProto = positionProto

    def get_field_value(self, field: FieldProto) -> object:
        """
        Returns the field value which could be any type, e.g. for Field.SECURITY a Security
        will be returned, but for Field.PORTFOLIO_ID a UUID would be returned.
        """
        return self.get_field(field_to_get=FieldMapEntry(field=field))

    def get_field(self, field_to_get: FieldMapEntry):
        """
        Returns the field value for the provided FieldMapEntry

        """
        tmp_field: FieldMapEntry

        # We'll iterate through the fields to make sure the requested field is in the proto.
        # If it's not then we'll raise a value error.
        for tmp_field in self.positionProto.fields:
            if tmp_field.field == field_to_get.field:
                if FieldProto.PORTFOLIO == field_to_get.field:
                    return Portfolio(Position.unpack_field(tmp_field))
                if FieldProto.SECURITY == field_to_get.field:
                    return Security(Position.unpack_field(tmp_field))

                unpacked_value = Position.unpack_field(tmp_field)

                if isinstance(unpacked_value, ProtoEnum):
                    descriptor = FieldProto.DESCRIPTOR.values_by_number[
                        field_to_get.field
                    ]
                    return ProtoEnum(descriptor, unpacked_value.enum_value)

                if (
                    isinstance(unpacked_value, str)
                    or isinstance(unpacked_value, float)
                    or isinstance(unpacked_value, int)
                ):
                    return unpacked_value

                return ProtoSerializationUtil.deserialize(unpacked_value)

        raise ValueError("Could not find field in position")

    def get_measure_value(self, measure: MeasureProto) -> Decimal:
        """
        Returns the decimal value for the measure
        """
        return self.get_measure(measure_to_get=MeasureMapEntry(measure=measure))

    def get_measure(self, measure_to_get: MeasureMapEntry) -> Decimal:
        """
        Returns the decimal for the given MeasureMapEntry

        """
        tmp_measure: MeasureMapEntry

        # We'll iterate through the measures to make sure the requested measure is in the proto.
        # If it's not then we'll raise a value error.
        for tmp_measure in self.positionProto.measures:
            if tmp_measure.measure == measure_to_get.measure:
                return ProtoSerializationUtil.deserialize(
                    Position.unpack_measure(tmp_measure)
                )

        raise ValueError("Could not find measure in position")

    def get_field_display(self, field_to_get: FieldMapEntry):
        field_value = self.get_field(field_to_get=field_to_get)
        return field_value.__str__()

    def get_measures(self) -> list[MeasureMapEntry]:
        return self.positionProto.measures

    def get_fields(self) -> list[FieldMapEntry]:
        return self.positionProto.fields

    def __str__(self):
        out: StringIO = StringIO()

        for field in self.get_fields():
            out.write(FieldProto.Name(number=field.field))
            out.write(",")
            out.write(self.get_field_display(field))
            out.write(";")

        for measure in self.get_measures():
            out.write(MeasureProto.Name(number=measure.measure))
            out.write(",")
            tmp: Decimal = self.get_measure(measure)
            out.write(str(tmp))
            out.write(";")

        return out.getvalue()

    @staticmethod
    def wrap_string_to_any(my_string: str):
        my_any = Any()
        my_any.Pack(wrappers.StringValue(value=my_string))
        return my_any

    @staticmethod
    def pack_field(field_to_pack):
        if field_to_pack.__class__ == LocalDateProto:
            my_any = Any()
            my_any.Pack(field_to_pack)
            return my_any

    @staticmethod
    def unpack_field(field_to_unpack: FieldMapEntry):
        if (
            field_to_unpack.field == FieldProto.PORTFOLIO_ID
            or field_to_unpack.field == FieldProto.SECURITY_ID
            or field_to_unpack.field == FieldProto.ID
        ):
            return UUIDProto.FromString(field_to_unpack.field_value_packed.value)
        if field_to_unpack.field == FieldProto.AS_OF:
            return LocalTimestampProto.FromString(
                field_to_unpack.field_value_packed.value
            )
        if (
            field_to_unpack.field == FieldProto.TRADE_DATE
            or field_to_unpack.field == FieldProto.MATURITY_DATE
            or field_to_unpack.field == FieldProto.ISSUE_DATE
            or field_to_unpack.field == FieldProto.SETTLEMENT_DATE
            or field_to_unpack.field == FieldProto.TAX_LOT_OPEN_DATE
            or field_to_unpack.field == FieldProto.TAX_LOT_CLOSE_DATE
        ):
            return LocalDateProto.FromString(field_to_unpack.field_value_packed.value)
        if field_to_unpack.field == FieldProto.IDENTIFIER:
            return IdentifierProto.FromString(field_to_unpack.field_value_packed.value)
        if (
            field_to_unpack.field == FieldProto.TRANSACTION_TYPE
            or field_to_unpack.field == FieldProto.POSITION_STATUS
        ):
            descriptor: str = FieldProto.DESCRIPTOR.values_by_number[
                field_to_unpack.field
            ]
            return ProtoEnum(descriptor, field_to_unpack.enum_value)
        if (
            field_to_unpack.field == FieldProto.PORTFOLIO_NAME
            or field_to_unpack.field == FieldProto.SECURITY_DESCRIPTION
            or field_to_unpack.field == FieldProto.PRODUCT_TYPE
            or field_to_unpack.field == FieldProto.ASSET_CLASS
        ):
            return wrappers.StringValue.FromString(
                field_to_unpack.field_value_packed.value
            ).value
        if field_to_unpack.field == FieldProto.PORTFOLIO:
            return PortfolioProto.FromString(field_to_unpack.field_value_packed.value)
        if field_to_unpack.field == FieldProto.SECURITY:
            return SecurityProto.FromString(field_to_unpack.field_value_packed.value)
        if (field_to_unpack.field == FieldProto.TENOR
            or field_to_unpack.field == FieldProto.ADJUSTED_TENOR):
            return TenorProto.FromString(field_to_unpack.field_value_packed.value)

        raise ValueError(
            f"Field not found. Could not unpack {FieldProto.Name(field_to_unpack.field)}"
        )

    from fintekkers.models.util.decimal_value_pb2 import DecimalValueProto

    @staticmethod
    def unpack_measure(measure_to_unpack: MeasureProto) -> DecimalValueProto:
        if measure_to_unpack.measure == MeasureProto.DIRECTED_QUANTITY:
            return measure_to_unpack.measure_decimal_value

        raise ValueError(
            f"Field not found. Could not unpack {MeasureProto.Name(measure_to_unpack.measure)}"
        )
