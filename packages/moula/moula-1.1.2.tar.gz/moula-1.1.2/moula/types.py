import datetime
import logging
from dataclasses import asdict, dataclass, field
from decimal import Decimal
from typing import List, Optional, Set

from moula.bootstrap import conf

logger = logging.getLogger(__name__)
ZERO = Decimal("0")
_LOCAL_CACHE: dict = {}


def is_liability(account_id=None, account=None):
    if account_id:
        return _LOCAL_CACHE[f"is-liabilities-{account_id}"]
    liability = account["attributes"]["type"] == "liabilities"
    _LOCAL_CACHE[f"is-liabilities-{account['id']}"] = liability


def set_default_cash_account(account):
    if conf.firefly.default_cash_account:
        return
    if account["attributes"]["type"] == "cash":
        logger.warning("setting default cash account to %r", account["id"])
        _LOCAL_CACHE["id"] = account["id"]


def get_default_cash_account():
    return conf.firefly.default_cash_account or _LOCAL_CACHE.get("id")


@dataclass
class Transaction:
    amount: Decimal
    date: datetime.date
    interest_date: datetime.date
    description: str
    remote_type: str
    currency_code: str

    _external_ids: Set[str] = field(default_factory=set)
    already_merged: bool = False

    source_id: Optional[str] = None
    destination_id: Optional[str] = None
    tags: Optional[List[str]] = None
    payment_date: Optional[datetime.date] = None

    @property
    def payload(self) -> dict:
        exclude_keys = {"_external_ids", "remote_type", "already_merged"}
        properties_to_include = {"type", "external_id"}
        payload = {
            key: value
            for key, value in asdict(self).items()
            if key not in exclude_keys and value
        }
        for key in properties_to_include:
            if getattr(self, key):
                payload[key] = getattr(self, key)
        for key, value in payload.items():
            if key in {"date", "payment_date", "interest_date"}:
                payload[key] = payload[key].isoformat()
        payload["amount"] = str(
            self.amount * (-1 if self.amount < ZERO else 1)
        )
        if payload.get("destination_id") is None:
            payload["destination_id"] = get_default_cash_account()
        if payload.get("source_id") is None:
            payload["source_id"] = get_default_cash_account()
        return payload

    def set_account_id(self, account_id):
        if self.amount < ZERO:
            self.source_id = account_id
        else:
            self.destination_id = account_id

    @property
    def external_id(self):
        return ".".join(sorted(ei for ei in self._external_ids if ei))

    @external_id.setter
    def external_id(self, value: str):
        for sub_value in value.split("."):
            self._external_ids.add(sub_value)

    @property
    def external_ids(self):
        return self._external_ids

    @property
    def type(self):
        if self.source_id and self.destination_id:
            return "transfer"
        if self.amount < ZERO:
            return "withdrawal"
        return "deposit"

    @property
    def is_mergeable(self) -> bool:
        return not self.already_merged

    def __repr__(self):
        msg = f"<Tr dt={self.date} {self.amount}€ "
        if self.source_id:
            msg += f"from={self.source_id} "
        if self.destination_id:
            msg += f"to={self.destination_id} "
        return msg + f"{self.description!r}>"

    def short_print(self, end="\n"):
        print(repr(self), end=end)


TRANSACTIONS = List[Transaction]
