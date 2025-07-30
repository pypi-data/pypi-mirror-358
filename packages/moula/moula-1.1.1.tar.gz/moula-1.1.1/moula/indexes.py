from decimal import Decimal
from typing import Dict, Optional, Tuple

from moula.types import TRANSACTIONS, Transaction
from moula.utils import ZERO, quantize

VectorKey = Tuple[Optional[str], Optional[str]]
IndexKey = Tuple[str, Decimal, VectorKey]
FireflyIndex = Dict[str, Dict[Decimal, Dict[VectorKey, list]]]
TransactionIndex = Dict[str, Dict[Decimal, Dict[VectorKey, list]]]
ExtIdIndex = Dict[str, Transaction]


def get_ff_keys(page) -> IndexKey:
    trs = page["attributes"]["transactions"]
    amount_key = sum((quantize(tr["amount"]) for tr in trs), ZERO)
    vector_key = (trs[0]["source_id"], trs[0]["destination_id"])
    return trs[0]["date"].split("T")[0], amount_key, vector_key


def get_tr_keys(tr: Transaction) -> IndexKey:
    date_key = getattr(tr, "date").isoformat()
    return date_key, tr.amount, (tr.source_id, tr.destination_id)


def feed_tr_indexes(
    transactions: TRANSACTIONS,
    transaction_index: TransactionIndex,
    ext_id_index: ExtIdIndex,
):
    for tr in transactions:
        date_key, amount_key, vector_key = get_tr_keys(tr)
        transaction_index[date_key][amount_key][vector_key].append(tr)
        for ext_id in tr.external_ids:
            ext_id_index[ext_id] = tr


def clean_tr_indexes(transactions: TRANSACTIONS, index: TransactionIndex):
    for tr in transactions:
        date_key, amount_key, vector_key = get_tr_keys(tr)
        tr_index = index[date_key][amount_key][vector_key]
        if tr in tr_index:
            tr_index.remove(tr)


def get_tr_by_ext_ids(ext_id_index: ExtIdIndex, page) -> TRANSACTIONS:
    ext_id_transactions: TRANSACTIONS = []
    for transaction in page["attributes"]["transactions"]:
        for ext_id in (transaction.get("external_id") or "").split("."):
            match = ext_id_index.get(ext_id) if ext_id else None
            if match and match not in ext_id_transactions:
                ext_id_transactions.append(ext_id_index[ext_id])
    return ext_id_transactions
