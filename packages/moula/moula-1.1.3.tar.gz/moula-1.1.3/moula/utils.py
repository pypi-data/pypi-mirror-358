from datetime import date
from decimal import Decimal
from moula.bootstrap import conf

ZERO = Decimal("0")
ACCURACY = Decimal(f".{'0' * (conf.accuracy - 1)}1")


def quantize(value: str) -> Decimal:
    return Decimal(value).quantize(ACCURACY)


def remove_double_space(words: str) -> str:
    while "  " in words:
        words = words.replace("  ", " ")
    return words


def french_date_to_iso(string: str, delimiter: str = "/") -> date:
    splits = string.split("/")
    return date(year=int(splits[2]), month=int(splits[1]), day=int(splits[0]))
