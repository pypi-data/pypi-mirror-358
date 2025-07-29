from typing import Literal, cast

TEProductFamily = Literal[
    "AV", "CloudResponse", "DarkWeb", "Essentials", "Legacy365Defense", "LogIC", "MDR", "Misc", "NICOS"
]

TE_PRODUCT_FAMILY_VALUES: set[TEProductFamily] = {
    "AV",
    "CloudResponse",
    "DarkWeb",
    "Essentials",
    "Legacy365Defense",
    "LogIC",
    "MDR",
    "Misc",
    "NICOS",
}


def check_te_product_family(value: str) -> TEProductFamily:
    if value in TE_PRODUCT_FAMILY_VALUES:
        return cast(TEProductFamily, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {TE_PRODUCT_FAMILY_VALUES!r}")
