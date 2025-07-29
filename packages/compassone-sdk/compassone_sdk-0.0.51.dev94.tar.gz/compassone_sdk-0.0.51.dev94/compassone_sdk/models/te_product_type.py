from typing import Literal, cast

TEProductType = Literal["AddOn", "NICOS", "Service"]

TE_PRODUCT_TYPE_VALUES: set[TEProductType] = {
    "AddOn",
    "NICOS",
    "Service",
}


def check_te_product_type(value: str) -> TEProductType:
    if value in TE_PRODUCT_TYPE_VALUES:
        return cast(TEProductType, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {TE_PRODUCT_TYPE_VALUES!r}")
