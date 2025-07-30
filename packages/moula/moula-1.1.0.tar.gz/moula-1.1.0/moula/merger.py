import logging
from datetime import timedelta
from typing import Generator, List

from moula.types import Transaction

logger = logging.getLogger(__name__)


def _merge_two(transaction_a: Transaction, transaction_b: Transaction):
    transaction_a.source_id = (
        transaction_a.source_id or transaction_b.source_id
    )
    transaction_a.destination_id = (
        transaction_a.destination_id or transaction_b.destination_id
    )
    for ext_id in transaction_a.external_ids.union(transaction_b.external_ids):
        transaction_a.external_id = ext_id
        transaction_b.external_id = ext_id
    transaction_a.already_merged = transaction_b.already_merged = True
    return transaction_a


def _iter_merged(
    mergeable_a: List[Transaction],
    mergeable_b: List[Transaction],
    delay: timedelta,
    comparison_key: str,
) -> Generator[Transaction, None, None]:
    for tr_a in mergeable_a:
        candidates = []
        for tr_b in mergeable_b:
            if not tr_b.is_mergeable or tr_a.amount != tr_b.amount * -1:
                continue
            lower = getattr(tr_b, comparison_key) - delay
            upper = getattr(tr_b, comparison_key) + delay
            if lower <= getattr(tr_a, comparison_key) <= upper:
                candidates.append(tr_b)
        if len(candidates) == 1:
            yield _merge_two(tr_a, candidates[0])
        elif len(candidates) > 1:
            candidates2 = [
                tr_b
                for tr_b in candidates
                if tr_b.source_id == tr_a.source_id
                or tr_b.destination_id == tr_a.destination_id
            ]
            if len(candidates2) == 1:
                yield _merge_two(tr_a, candidates[0])
            elif candidates2:
                logger.error(
                    "too many candidates %r (for %r)", candidates2, candidates
                )


def merge(
    transactions_a: List[Transaction],
    transactions_b: List[Transaction],
    delay: timedelta = timedelta(days=0),
    comparison_key: str = "date",
) -> Generator[Transaction, None, None]:
    mergeable_a: List[Transaction] = []
    mergeable_b: List[Transaction] = []

    # purging
    for iterator, buffer in [
        (transactions_a, mergeable_a),
        (transactions_b, mergeable_b),
    ]:
        for transaction in iterator:
            if transaction.is_mergeable:
                buffer.append(transaction)
    yield from _iter_merged(mergeable_a, mergeable_b, delay, comparison_key)

    merged = 0
    for tr_b in mergeable_b:
        if not tr_b.is_mergeable:
            merged += 1
    logger.debug(
        "merging list a(%d) and b(%d) with %d and %d mergeable result"
        "ing in %d merged",
        len(transactions_a),
        len(transactions_b),
        len(mergeable_a),
        len(mergeable_b),
        merged,
    )
