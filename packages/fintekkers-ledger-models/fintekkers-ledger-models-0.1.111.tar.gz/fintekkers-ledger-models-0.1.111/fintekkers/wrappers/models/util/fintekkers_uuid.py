from uuid import UUID, uuid4


class FintekkersUuid:
    uuid: UUID

    def __init__(self, uuid: UUID):
        self.uuid = uuid

    def __str__(self) -> str:
        return self.uuid.__str__()

    @staticmethod
    def from_uuid(uuid: UUID):
        return FintekkersUuid(uuid)

    @staticmethod
    def from_bytes(raw_uuid: list[bytes]):
        return FintekkersUuid(UUID(bytes=raw_uuid))

    @staticmethod
    def new_uuid():
        return FintekkersUuid(uuid4())

    def as_uuid(self) -> UUID:
        return self.uuid

    def as_bytes(self) -> list[bytes]:
        return self.uuid.bytes
