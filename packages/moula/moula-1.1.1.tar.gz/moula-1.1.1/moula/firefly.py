import logging
from collections import defaultdict
from typing import Any, Dict, Generator, List, Optional, Tuple

import requests

from moula import indexes
from moula.bootstrap import conf
from moula.types import (
    TRANSACTIONS,
    get_default_cash_account,
    is_liability,
    set_default_cash_account,
)
from moula.utils import ZERO

logger = logging.getLogger(__name__)
FireflyTransaction = Dict
FireflyTransactions = List[FireflyTransaction]
Command = Tuple[str, Optional[str], Optional[Dict]]
Commands = Generator[Command, None, None]


def query(
    method: str,
    endpoint: str,
    params: Optional[Dict[str, str]] = None,
    body: Optional[Dict[str, Any]] = None,
):
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {conf.firefly.token}",
    }
    response = requests.request(
        method=method,
        headers=headers,
        url=f"{conf.firefly.url}/api/v1/{endpoint.lstrip('/')}",
        params=params,
        json=body,
        timeout=60,
    )
    response.raise_for_status()
    return response.json()


def paginate(
    method: str,
    endpoint: str,
    params: Optional[Dict[str, str]] = None,
    body: Optional[Dict[str, Any]] = None,
):
    params = params or {}
    page = 1
    one_more_page = True
    while one_more_page:
        result = query(method, endpoint, params, body)
        yield from result["data"]
        page += 1
        pagination = result["meta"]["pagination"]
        params["page"] = str(page)
        one_more_page = pagination["current_page"] < pagination["total_pages"]
        if pagination["current_page"] % 20 == 0:
            logger.debug(
                "browsed %d/%d pages",
                pagination["current_page"],
                pagination["total_pages"],
            )


def browse_accounts():
    logger.debug("fetching firefly accounts")
    facc_ids = {}
    for firefly_acc in paginate("get", "accounts"):
        if firefly_acc["attributes"]["account_number"]:
            facc_ids[firefly_acc["attributes"]["account_number"]] = firefly_acc
        if firefly_acc["attributes"]["type"] == "cash":
            set_default_cash_account(firefly_acc)
        is_liability(account=firefly_acc)
    logger.info("got %d accounts from firefly", len(facc_ids))
    return facc_ids


def __fix_title(body, transactions, candidate, existings, transaction_ids):
    cand_desc = candidate["description"]
    if len(transaction_ids) > 1 and existings[0]["attributes"].get(
        "group_title"
    ):
        existing_desc = existings[0]["attributes"]["group_title"]
    else:
        existing_desc = existings[0]["attributes"]["transactions"][0][
            "description"
        ]
    if existing_desc != cand_desc and len(cand_desc) > len(existing_desc):
        if len(transaction_ids) > 1:
            body["group_title"] = cand_desc
        elif transactions:
            transactions[0]["description"] = cand_desc
        else:
            transactions.append(
                {
                    "transaction_journal_id": transaction_ids[0],
                    "description": cand_desc,
                }
            )


def _manage_existing(
    candidates: TRANSACTIONS, existings: FireflyTransactions
) -> Commands:
    cash_account = get_default_cash_account()
    if len(candidates) == 1:
        candidate = candidates[0].payload
        body: Dict = {}
        transactions = []
        transaction_ids = [
            transaction["transaction_journal_id"]
            for transaction in existings[0]["attributes"]["transactions"]
        ]
        for transaction_id in transaction_ids:
            ffly = [
                transaction
                for transaction in existings[0]["attributes"]["transactions"]
                if transaction["transaction_journal_id"] == transaction_id
            ][0]

            for key in "source_id", "destination_id":
                no_value = not ffly.get(key) or ffly[key] == "0"
                if no_value:
                    transactions.append(
                        {
                            key: candidate[key],
                            "transaction_journal_id": transaction_id,
                            "type": candidate["type"],
                        }
                    )
                elif (
                    cash_account
                    and ffly[key] == cash_account
                    and candidate[key] != cash_account
                ):
                    transactions.append(
                        {
                            key: candidate[key],
                            "transaction_journal_id": transaction_id,
                            "type": candidate["type"],
                        }
                    )
        __fix_title(body, transactions, candidate, existings, transaction_ids)
        if body or transactions:
            if transactions:
                body["transactions"] = transactions
            yield "update", existings[0]["id"], body
        else:
            yield ".", None, None
    else:
        yield "x", None, None


def iter_operations(
    existings: FireflyTransactions, candidates: TRANSACTIONS
) -> Commands:
    if not existings:
        # no existing, we must create them all
        for candidate in candidates:
            payload = candidate.payload
            # manage firefly quirk, can't have transfer with liability account
            if payload["type"] == "transfer":
                if is_liability(payload["source_id"]):
                    payload["type"] = "deposit"
                elif is_liability(payload["destination_id"]):
                    payload["type"] = "withdrawal"
            yield "create", None, {"transactions": [payload]}
    elif len(candidates) < len(existings):
        # more existing than candidate, can't compare (maybe access to
        # previous records has been loast
        yield "u", None, None
    elif len(candidates) == len(existings):
        # same number, we should be able to match them against
        # one another
        yield from _manage_existing(candidates, existings)
    else:
        # at least one existing, but more candidates than existing
        # not supported yet, need to implement incremental intra day
        # push
        logger.debug(
            "got %d candidates for %d existing:\n%r\n%r",
            len(candidates),
            len(existings),
            "\n".join(map(repr, candidates)),
            "\n".join(map(repr, existings)),
        )
        yield "!", None, None


def _get_ff_filters(transactions: TRANSACTIONS):
    dates = []
    for transaction in transactions:
        dates.append(transaction.interest_date)
        dates.append(transaction.date)
    return {"start": min(dates).isoformat(), "end": max(dates).isoformat()}


def get_transactions_to_push(transactions: TRANSACTIONS) -> Commands:
    logger.debug("fetching existing records")
    index: indexes.FireflyIndex = defaultdict(
        lambda: defaultdict(lambda: defaultdict(list))
    )
    ext_id_index: indexes.ExtIdIndex = {}
    transaction_index: indexes.TransactionIndex = defaultdict(
        lambda: defaultdict(lambda: defaultdict(list))
    )

    indexes.feed_tr_indexes(transactions, transaction_index, ext_id_index)

    existing_count = 0
    for page in paginate(
        "get", "transactions", params=_get_ff_filters(transactions)
    ):
        existing_count += 1
        date_key, amount_key, vector_key = indexes.get_ff_keys(page)
        if ext_id_trs := indexes.get_tr_by_ext_ids(ext_id_index, page):
            yield from iter_operations([page], ext_id_trs)
            indexes.clean_tr_indexes(ext_id_trs, transaction_index)
        else:
            index[date_key][amount_key][vector_key].append(page)

    logger.info("got %d exiting records", existing_count)
    for current_date in sorted(transaction_index):
        for amount, trans_by_vector in transaction_index[current_date].items():
            amount = amount * -1 if amount < ZERO else amount
            current_index = index[current_date][amount]
            no_source: Dict[str, TRANSACTIONS] = defaultdict(list)
            no_destination: Dict[str, TRANSACTIONS] = defaultdict(list)
            processed_keys = set()
            for (src_id, dst_id), candidates in trans_by_vector.items():
                if dst_id and src_id is None:
                    no_source[dst_id].extend(candidates)
                elif src_id and dst_id is None:
                    no_destination[src_id].extend(candidates)
                else:
                    processed_keys.add((src_id, dst_id))
                    yield from iter_operations(
                        current_index[(src_id, dst_id)], candidates
                    )
            existings: List[Dict]
            for dst_id, candidates in no_source.items():
                existings = sum(
                    [
                        existing
                        for (
                            esrc_id,
                            edst_id,
                        ), existing in current_index.items()
                        if edst_id == dst_id
                        and (esrc_id, edst_id) not in processed_keys
                    ],
                    [],
                )
                yield from iter_operations(existings, candidates)
            for src_id, candidates in no_destination.items():
                existings = sum(
                    [
                        existing
                        for (
                            esrc_id,
                            edst_id,
                        ), existing in current_index.items()
                        if esrc_id == src_id
                        and (esrc_id, edst_id) not in processed_keys
                    ],
                    [],
                )
                yield from iter_operations(existings, candidates)


def log_body(verb, body, firefly_id=None):
    message = f"{verb} <Tr"
    if firefly_id:
        message += f" {firefly_id}"
    if body.get("group_title"):
        message += f" description={body['group_title']!r}"
    if body.get("transactions"):
        for key, new_value in body["transactions"][0].items():
            message += f" {key}={new_value!r}"
    message += ">"
    logger.warning(message)


def push(transactions: TRANSACTIONS, dry_run: bool = False):
    to_push = list(get_transactions_to_push(transactions))
    if any(operation == "!" for operation, _, _ in to_push):
        logger.fatal("unruly records, aborting!")
        return
    created = updated = 0
    for operation, firefly_id, body in to_push:
        if operation == "create":
            log_body("creating", body)
            if not dry_run:
                query("post", "transactions", body=body)
                created += 1
        elif operation == "update":
            log_body("updating", body, firefly_id)
            if not dry_run:
                query("put", f"transactions/{firefly_id}", body=body)
                updated += 1
    logger.info("created %d new records, updated %d", created, updated)
