import time
from datetime import date, datetime
from uuid import uuid4
from google.protobuf.any_pb2 import Any
from google.protobuf.timestamp_pb2 import Timestamp

from fintekkers.models.position.field_pb2 import FieldProto
from fintekkers.models.position.position_filter_pb2 import PositionFilterProto
from fintekkers.models.position.position_util_pb2 import FieldMapEntry
from fintekkers.models.security.coupon_frequency_pb2 import NO_COUPON, SEMIANNUALLY
from fintekkers.models.security.coupon_type_pb2 import FIXED, FLOAT, ZERO
from fintekkers.models.security.identifier.identifier_pb2 import IdentifierProto
from fintekkers.models.security.identifier.identifier_type_pb2 import CUSIP
from fintekkers.models.security.security_pb2 import SecurityProto
from fintekkers.models.security.security_quantity_type_pb2 import ORIGINAL_FACE_VALUE
from fintekkers.models.security.security_type_pb2 import (
    BOND_SECURITY,
    FRN,
    SecurityTypeProto,
)
from fintekkers.models.util.local_timestamp_pb2 import LocalTimestampProto
from fintekkers.models.util.uuid_pb2 import UUIDProto

from fintekkers.models.security.bond.issuance_pb2 import IssuanceProto

from fintekkers.requests.security.create_security_request_pb2 import (
    CreateSecurityRequestProto,
)
from fintekkers.requests.security.query_security_request_pb2 import (
    QuerySecurityRequestProto,
)

from fintekkers.wrappers.models.security.security import Security
from fintekkers.wrappers.models.util.date_utils import get_date_proto
from fintekkers.wrappers.models.util.serialization import ProtoSerializationUtil


class CreateSecurityRequest:
    @staticmethod
    def create_ust_security_request(
        cusip: str,
        cash_security: SecurityProto,
        security_type: SecurityTypeProto = SecurityTypeProto.BOND_SECURITY,
        coupon_rate: float = 0.0,
        spread: float = 0.0,
        face_value: float = 0.0,
        issue_date: date = date.today(),
        dated_date: date = date.today(),
        maturity_date: date = date.today(),
        post_auction_outstanding_quantity: float = 0.0,
        auction_total_accepted: float = 0.0,
        auction_announcement_date: date = None,
    ):
        """
        Creates a request to create a security representing a US treasury (bills, notes and bonds)

            Parameters:
                    Parameters are already in protos, see type hints. Post auction quantity refers to the
                    amount of the security that existed after the auction of this security (for re-issues).
                    Total accepted refers to the amount of bond that was sold at the auction.

            Returns:
                    request (CreateSecurityRequest): A request wrapper, with the fields attached
        """
        id = IdentifierProto(identifier_type=CUSIP, identifier_value=cusip)

        security_type = BOND_SECURITY
        coupon_frequency = SEMIANNUALLY
        coupon_type = FIXED

        # if security_type == TIPS:
        #     security_type = TIPS
        if security_type == FRN:
            # security_type = FRN
            coupon_type = FLOAT
            coupon_rate = spread
        if security_type == ZERO:
            coupon_type = ZERO
            coupon_frequency = NO_COUPON

        issue_date_proto = get_date_proto(issue_date)
        dated_date_proto = get_date_proto(dated_date) if dated_date != None else None
        maturity_date_proto = get_date_proto(maturity_date)

        timstamp_seconds = int(time.mktime(issue_date.timetuple()))

        issuance_list = []

        if auction_announcement_date is not None:
            issuance = IssuanceProto(
                as_of=LocalTimestampProto(
                    time_zone="America/New_York",
                    timestamp=Timestamp(seconds=timstamp_seconds, nanos=0),
                ),
                version="0.0.1",
                auction_announcement_date=ProtoSerializationUtil.serialize(
                    auction_announcement_date
                ),
                total_accepted=ProtoSerializationUtil.serialize(auction_total_accepted),
                post_auction_outstanding_quantity=ProtoSerializationUtil.serialize(
                    post_auction_outstanding_quantity
                ),
            )
            issuance_list.append(issuance)

        security_proto: SecurityProto = SecurityProto(
            as_of=LocalTimestampProto(
                time_zone="America/New_York",
                timestamp=Timestamp(seconds=timstamp_seconds, nanos=0),
            ),
            uuid=UUIDProto(raw_uuid=uuid4().bytes),
            issuer_name="US Government",
            identifier=id,
            issue_date=issue_date_proto,
            dated_date=dated_date_proto,
            maturity_date=maturity_date_proto,
            security_type=security_type,
            quantity_type=ORIGINAL_FACE_VALUE,
            settlement_currency=cash_security,
            coupon_frequency=coupon_frequency,
            coupon_type=coupon_type,
            coupon_rate=ProtoSerializationUtil.serialize(coupon_rate),
            asset_class="Fixed Income",
            face_value=ProtoSerializationUtil.serialize(face_value),
            issuance_info=issuance_list,
        )

        security = Security(security_proto)

        return CreateSecurityRequest.create_or_update_request(security)

    @staticmethod
    def create_or_update_request(security: Security):
        proto: CreateSecurityRequestProto = CreateSecurityRequestProto(
            security_input=security.proto
        )

        return CreateSecurityRequest(proto=proto)

    def __init__(self, proto: CreateSecurityRequestProto):
        self.proto = proto


class QuerySecurityRequest:
    @staticmethod
    def create_query_request(fields: dict):
        """
        Returns a query request from a dict of field/values

                Parameters:
                        fields (dict): A dictionary of fields with values

                Returns:
                        request (QuerySecurityRequest): A request wrapper, with the fields attached. It assumes that all filters are an equals operation
        """

        filters = []

        for field in fields:
            field: FieldProto

            field_value = fields[field]

            if isinstance(field_value, str):
                entry = FieldMapEntry(field=field, string_value=field_value)
            else:
                packed_value: Any = Any()
                packed_value.Pack(msg=field_value)
                entry = FieldMapEntry(field=field, field_value_packed=packed_value)

            filters.append(entry)

        as_of_proto: LocalTimestampProto = ProtoSerializationUtil.serialize(
            datetime.now()
        )

        request: QuerySecurityRequestProto = QuerySecurityRequestProto(
            search_security_input=PositionFilterProto(filters=filters),
            as_of=as_of_proto,
        )

        return QuerySecurityRequest(proto=request)

    def __init__(self, proto: CreateSecurityRequestProto):
        self.proto = proto
