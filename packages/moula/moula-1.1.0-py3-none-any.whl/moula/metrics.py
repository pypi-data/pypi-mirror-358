from prometheus_client import Gauge
from moula.bootstrap import conf

positions = Gauge(
    "financial_positions",
    "",
    [
        "bank",
        "account_type",
        "account_name",
        "account_id",
        "line_name",
        "line_id",
        "value_type",
    ],
    namespace=conf.prometheus.namespace,
)
