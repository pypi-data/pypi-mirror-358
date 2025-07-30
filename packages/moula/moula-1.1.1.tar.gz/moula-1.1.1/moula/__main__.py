#!/usr/bin/env python
import logging
import time
from collections import defaultdict
from datetime import date, timedelta
from itertools import product

import daemon_metrics
from prometheus_client import start_http_server

from moula import firefly, woob
from moula.bootstrap import conf
from moula.merger import merge

logger = logging.getLogger("moula")
try:
    logger.setLevel(getattr(logging, conf.logging.level.upper()))
    logger.addHandler(logging.StreamHandler())
except AttributeError as error:
    raise AttributeError(
        f"{conf.logging.level} isn't accepted, only DEBUG, INFO, WARNING, "
        "ERROR and FATAL are accepted"
    ) from error


def iter_accounts():
    facc_ids = firefly.browse_accounts()
    for backend, account in woob.get_accounts():
        if account.id not in facc_ids:
            continue
        yield facc_ids[account.id], backend, account
        daemon_metrics.item_result(conf.name, False, account.id)


def get_all_transactions():
    transactions = defaultdict(list)
    final = []
    for firefly_account, woob_backend, account in iter_accounts():
        for transaction in woob.get_transactions(
            woob_backend,
            account,
            firefly_account["attributes"]["name"],
            firefly_account["id"],
        ):
            transactions[firefly_account["id"]].append(transaction)
        daemon_metrics.item_result(
            conf.name, bool(transactions[firefly_account["id"]]), account.id
        )
    for date_key in "date", "interest_date":
        pairs = {tuple(sorted(p)) for p in product(transactions, repeat=2)}
        for account1, account2 in sorted(pairs):
            if account1 == account2:
                continue
            logger.debug("processing account %r and %r", account1, account2)
            for transaction in merge(
                transactions[account1],
                transactions[account2],
                delay=timedelta(days=conf.merge_date_tolerance),
                comparison_key=date_key,
            ):
                final.append(transaction)
    for tr_list in transactions.values():
        for transaction in tr_list:
            if not transaction.already_merged:
                final.append(transaction)
    return sorted(final, key=lambda transaction: transaction.date)


def main():
    info = {
        "loop-perid": conf.loop.interval,
        "loop-lookback": conf.loop.lookback,
        "item-count": len(list(iter_accounts())),
    }
    daemon_metrics.init(conf.name, info)

    while True:
        loop_context = daemon_metrics.LoopContext(conf.name)
        with loop_context:
            if conf.firefly.lookback:
                logger.info(
                    "will only consider data for the last %d days",
                    conf.firefly.lookback,
                )
            transactions = get_all_transactions()
            if conf.firefly.lookback:
                limit = date.today() - timedelta(days=conf.firefly.lookback)
                transactions = [
                    transaction
                    for transaction in transactions
                    if transaction.date >= limit
                ]
            firefly.push(transactions, dry_run=not conf.firefly.push)

        if (interval := conf.loop.interval - loop_context.exec_interval) > 0:
            time.sleep(interval)

        if not conf.loop.enabled:
            break


if __name__ == "__main__":
    logger.info("Starting moula")
    start_http_server(conf.prometheus.port)
    main()
