import logging
from datetime import date, datetime
from decimal import Decimal
from functools import partial
from typing import Generator, Union

from moula.metrics import positions
from moula.types import Transaction
from moula.utils import ACCURACY
from woob.capabilities import NotAvailable
from woob.capabilities.bank import CapBank
from woob.core import Woob
from woob.exceptions import BrowserUnavailable

logger = logging.getLogger(__name__)
INV_ACC_TYPES = {"LIFE_INSURANCE", "PEA", "MARKET", "PERP"}


def get_date(dt: Union[date, datetime]) -> date:
    if isinstance(dt, date) and not isinstance(dt, datetime):
        return dt
    return dt.date()


def get_type_name(woob_item) -> str:
    return {
        getattr(woob_item, key): key[5:]
        for key in dir(woob_item)
        if key.startswith("TYPE_")
    }.get(woob_item.type) or ""


def to_transaction(account_id, woob_transaction) -> Transaction:
    remote_type = get_type_name(woob_transaction).lower()
    tr_source_id = tr_destination_id = None
    tags = []
    if woob_transaction.amount < Decimal("0"):
        tr_source_id = account_id
    else:
        tr_destination_id = account_id
    if remote_type != "transfer":
        tags.append(remote_type)

    transaction = Transaction(
        description=woob_transaction.label,
        date=get_date(woob_transaction.date),
        payment_date=get_date(woob_transaction.rdate),
        interest_date=get_date(woob_transaction.vdate),
        currency_code="EUR",
        amount=woob_transaction.amount,
        tags=tags,
        remote_type=remote_type,
        destination_id=tr_destination_id,
        source_id=tr_source_id,
    )
    if woob_transaction.id:
        transaction.external_id = woob_transaction.id
    return transaction


def get_account_type(account) -> str:
    return {
        getattr(account, key): key[5:]
        for key in dir(account)
        if key.startswith("TYPE_")
    }.get(account.type) or ""


def get_line_position(backend, account_type, account):
    def wrapped(line_name, line_id, value_type, value):
        args = (
            backend.name.upper() if backend.name else "",
            account_type,
            account.label or "",
            account.id or "",
            line_name if line_name != NotAvailable else "",
            line_id if line_id != NotAvailable else "",
            value_type,
        )
        logger.debug("seeing %s %s %s %s: %s, %s (%s) => %s", *args, value)
        return positions.labels(*args).set(value)

    return wrapped


def investments_metrics(backend, account, line_position):
    try:
        for inv in backend.iter_investment(account):
            inv_position = partial(line_position, inv.label, inv.code)
            if not inv.valuation:
                continue
            inv_position("valuation", inv.valuation)
            if inv.quantity:
                inv_position("quantity", inv.quantity)
            if inv.unitvalue:
                inv_position("par-value", inv.unitvalue)
            if not inv.diff_ratio:
                continue
            gain = inv.valuation - (inv.valuation / (inv.diff_ratio + 1))
            gain = gain.quantize(ACCURACY)
            inv_position("gain-percent", inv.diff_ratio * 100)
            inv_position("gain", gain)
    except NotImplementedError:
        logger.debug(
            "%r:%r does not support itering on accounts", backend, account
        )
    except Exception:
        logger.error(
            "%r:%r error while fetching investments", backend, account
        )


def get_accounts():
    for backend in Woob().load_backends(CapBank).values():
        try:
            for account in backend.iter_accounts():
                acc_type = get_account_type(account)
                line_position = get_line_position(backend, acc_type, account)
                line_position(
                    "balance", "balance", "valuation", account.balance
                )
                yield backend, account
                if acc_type not in INV_ACC_TYPES:
                    continue
                investments_metrics(backend, account, line_position)
        except (BrowserUnavailable, NotImplementedError):
            logger.debug("%r does not support itering on accounts", backend)
        except Exception:
            logger.exception("%r error while itering on accounts", backend)


def get_transactions(
    backend,
    account,
    account_name: str,
    account_id: str,
) -> Generator[Transaction, None, None]:
    logger.debug("getting transaction for %s:%s", backend.name, account_name)
    total = 0
    try:
        for woob_transaction in backend.iter_history(account):
            total += 1
            yield to_transaction(account_id, woob_transaction)
    except NotImplementedError:
        return
    logger.info(
        "got %d transactions for %s:%s", total, backend.name, account_name
    )
