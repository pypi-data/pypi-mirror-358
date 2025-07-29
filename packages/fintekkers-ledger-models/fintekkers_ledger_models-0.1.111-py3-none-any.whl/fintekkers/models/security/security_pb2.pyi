from fintekkers.models.util import decimal_value_pb2 as _decimal_value_pb2
from fintekkers.models.util import local_date_pb2 as _local_date_pb2
from fintekkers.models.util import local_timestamp_pb2 as _local_timestamp_pb2
from fintekkers.models.util import uuid_pb2 as _uuid_pb2
from fintekkers.models.security.identifier import identifier_pb2 as _identifier_pb2
from fintekkers.models.security.bond import issuance_pb2 as _issuance_pb2
from fintekkers.models.security import security_type_pb2 as _security_type_pb2
from fintekkers.models.security import security_quantity_type_pb2 as _security_quantity_type_pb2
from fintekkers.models.security import coupon_frequency_pb2 as _coupon_frequency_pb2
from fintekkers.models.security import coupon_type_pb2 as _coupon_type_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SecurityProto(_message.Message):
    __slots__ = ("object_class", "version", "uuid", "as_of", "is_link", "valid_from", "valid_to", "security_type", "asset_class", "issuer_name", "settlement_currency", "quantity_type", "identifier", "description", "cash_id", "coupon_rate", "coupon_type", "coupon_frequency", "dated_date", "face_value", "issue_date", "maturity_date", "issuance_info")
    OBJECT_CLASS_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    UUID_FIELD_NUMBER: _ClassVar[int]
    AS_OF_FIELD_NUMBER: _ClassVar[int]
    IS_LINK_FIELD_NUMBER: _ClassVar[int]
    VALID_FROM_FIELD_NUMBER: _ClassVar[int]
    VALID_TO_FIELD_NUMBER: _ClassVar[int]
    SECURITY_TYPE_FIELD_NUMBER: _ClassVar[int]
    ASSET_CLASS_FIELD_NUMBER: _ClassVar[int]
    ISSUER_NAME_FIELD_NUMBER: _ClassVar[int]
    SETTLEMENT_CURRENCY_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_TYPE_FIELD_NUMBER: _ClassVar[int]
    IDENTIFIER_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    CASH_ID_FIELD_NUMBER: _ClassVar[int]
    COUPON_RATE_FIELD_NUMBER: _ClassVar[int]
    COUPON_TYPE_FIELD_NUMBER: _ClassVar[int]
    COUPON_FREQUENCY_FIELD_NUMBER: _ClassVar[int]
    DATED_DATE_FIELD_NUMBER: _ClassVar[int]
    FACE_VALUE_FIELD_NUMBER: _ClassVar[int]
    ISSUE_DATE_FIELD_NUMBER: _ClassVar[int]
    MATURITY_DATE_FIELD_NUMBER: _ClassVar[int]
    ISSUANCE_INFO_FIELD_NUMBER: _ClassVar[int]
    object_class: str
    version: str
    uuid: _uuid_pb2.UUIDProto
    as_of: _local_timestamp_pb2.LocalTimestampProto
    is_link: bool
    valid_from: _local_timestamp_pb2.LocalTimestampProto
    valid_to: _local_timestamp_pb2.LocalTimestampProto
    security_type: _security_type_pb2.SecurityTypeProto
    asset_class: str
    issuer_name: str
    settlement_currency: SecurityProto
    quantity_type: _security_quantity_type_pb2.SecurityQuantityTypeProto
    identifier: _identifier_pb2.IdentifierProto
    description: str
    cash_id: str
    coupon_rate: _decimal_value_pb2.DecimalValueProto
    coupon_type: _coupon_type_pb2.CouponTypeProto
    coupon_frequency: _coupon_frequency_pb2.CouponFrequencyProto
    dated_date: _local_date_pb2.LocalDateProto
    face_value: _decimal_value_pb2.DecimalValueProto
    issue_date: _local_date_pb2.LocalDateProto
    maturity_date: _local_date_pb2.LocalDateProto
    issuance_info: _containers.RepeatedCompositeFieldContainer[_issuance_pb2.IssuanceProto]
    def __init__(self, object_class: _Optional[str] = ..., version: _Optional[str] = ..., uuid: _Optional[_Union[_uuid_pb2.UUIDProto, _Mapping]] = ..., as_of: _Optional[_Union[_local_timestamp_pb2.LocalTimestampProto, _Mapping]] = ..., is_link: bool = ..., valid_from: _Optional[_Union[_local_timestamp_pb2.LocalTimestampProto, _Mapping]] = ..., valid_to: _Optional[_Union[_local_timestamp_pb2.LocalTimestampProto, _Mapping]] = ..., security_type: _Optional[_Union[_security_type_pb2.SecurityTypeProto, str]] = ..., asset_class: _Optional[str] = ..., issuer_name: _Optional[str] = ..., settlement_currency: _Optional[_Union[SecurityProto, _Mapping]] = ..., quantity_type: _Optional[_Union[_security_quantity_type_pb2.SecurityQuantityTypeProto, str]] = ..., identifier: _Optional[_Union[_identifier_pb2.IdentifierProto, _Mapping]] = ..., description: _Optional[str] = ..., cash_id: _Optional[str] = ..., coupon_rate: _Optional[_Union[_decimal_value_pb2.DecimalValueProto, _Mapping]] = ..., coupon_type: _Optional[_Union[_coupon_type_pb2.CouponTypeProto, str]] = ..., coupon_frequency: _Optional[_Union[_coupon_frequency_pb2.CouponFrequencyProto, str]] = ..., dated_date: _Optional[_Union[_local_date_pb2.LocalDateProto, _Mapping]] = ..., face_value: _Optional[_Union[_decimal_value_pb2.DecimalValueProto, _Mapping]] = ..., issue_date: _Optional[_Union[_local_date_pb2.LocalDateProto, _Mapping]] = ..., maturity_date: _Optional[_Union[_local_date_pb2.LocalDateProto, _Mapping]] = ..., issuance_info: _Optional[_Iterable[_Union[_issuance_pb2.IssuanceProto, _Mapping]]] = ...) -> None: ...
