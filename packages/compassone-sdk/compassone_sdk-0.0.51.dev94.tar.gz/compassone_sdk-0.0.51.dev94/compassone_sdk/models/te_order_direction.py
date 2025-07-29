from typing import Literal, cast

TEOrderDirection = Literal["ASC", "DESC"]

TE_ORDER_DIRECTION_VALUES: set[TEOrderDirection] = {
    "ASC",
    "DESC",
}


def check_te_order_direction(value: str) -> TEOrderDirection:
    if value in TE_ORDER_DIRECTION_VALUES:
        return cast(TEOrderDirection, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {TE_ORDER_DIRECTION_VALUES!r}")
