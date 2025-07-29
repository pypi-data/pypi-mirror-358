from datetime import datetime
from uuid import uuid4, UUID

from google.protobuf.timestamp_pb2 import Timestamp
from fintekkers.models.price.price_pb2 import PriceProto
from fintekkers.models.util.local_timestamp_pb2 import LocalTimestampProto
from fintekkers.models.util.uuid_pb2 import UUIDProto
from fintekkers.wrappers.models.security.security import Security
from fintekkers.wrappers.models.util.fintekkers_uuid import FintekkersUuid
from fintekkers.wrappers.models.util.serialization import ProtoSerializationUtil


class Price:
    def __init__(self, proto: PriceProto):
        self.proto: PriceProto = proto

    def __str__(self):
        return f"ID[{self.get_uuid()}], Price[{self.get_price()}]"

    def get_price(self) -> float:
        price:float = ProtoSerializationUtil.deserialize(self.proto.price)
        return price

    def get_as_of(self) -> datetime:
        as_of: LocalTimestampProto = ProtoSerializationUtil.deserialize(self.proto.as_of)
        return as_of

    def get_uuid(self) -> UUID:
        uuid: FintekkersUuid = ProtoSerializationUtil.deserialize(self.proto.uuid)
        return uuid.as_uuid()


    @staticmethod
    def create_price(security:Security, price: float, as_of_date:Timestamp):
        uuid_value = uuid4()

        price = PriceProto(
            as_of=LocalTimestampProto(
                timestamp=as_of_date, time_zone="America/New_York"
            ),
            is_link=False,
            object_class="Portfolio",
            uuid=UUIDProto(raw_uuid=uuid_value.bytes),
            price=ProtoSerializationUtil.serialize(price),
            security=security.proto,
            version="0.0.1",
        )

        return Price(price)
