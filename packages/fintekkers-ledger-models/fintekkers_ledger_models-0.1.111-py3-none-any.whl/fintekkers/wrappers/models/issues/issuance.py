from datetime import date
from fintekkers.models.security.bond.issuance_pb2 import IssuanceProto
from fintekkers.wrappers.models.util.serialization import ProtoSerializationUtil


class Issuance:
    def __init__(self, proto: list[IssuanceProto]):
        self.proto: list[IssuanceProto] = proto

    def sort_by_auction_announcement_date(self):
        self.proto = sorted(
            self.proto,
            key=lambda x: ProtoSerializationUtil.deserialize(
                x.auction_announcement_date
            ),
        )
        return self

    def print_auction_history(self):
        print(
            "announcement_date,mature_security_amount,total_accepted,post_auction_outstanding_quantity"
        )

        for issue in self.proto:
            issue: IssuanceProto

            auction_announcement_date: date = ProtoSerializationUtil.deserialize(
                issue.auction_announcement_date
            )
            mature_security_amount = 0.0
            total_accepted = 0.0
            post_auction_outstanding_quantity = 0.0

            if (
                issue.mature_security_amount is not None
                and issue.mature_security_amount.arbitrary_precision_value != ""
            ):
                mature_security_amount: float = ProtoSerializationUtil.deserialize(
                    issue.mature_security_amount
                )

            if (
                issue.total_accepted is not None
                and issue.total_accepted.arbitrary_precision_value != ""
            ):
                total_accepted: float = ProtoSerializationUtil.deserialize(
                    issue.total_accepted
                )

            if (
                issue.post_auction_outstanding_quantity is not None
                and issue.post_auction_outstanding_quantity.arbitrary_precision_value
                != ""
            ):
                post_auction_outstanding_quantity: float = (
                    ProtoSerializationUtil.deserialize(
                        issue.post_auction_outstanding_quantity
                    )
                )

            print(
                "{},${:,.2f},${:,.2f},${:,.2f}".format(
                    auction_announcement_date,
                    mature_security_amount,
                    total_accepted,
                    post_auction_outstanding_quantity,
                )
            )
