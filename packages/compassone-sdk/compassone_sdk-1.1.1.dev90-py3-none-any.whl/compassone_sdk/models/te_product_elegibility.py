from typing import Literal, cast

TEProductElegibility = Literal[
    "BpResponseAndCompliance", "CloudResponseStandalone", "DarkWeb", "Default", "Essentials", "MDRPromotion", "MSP"
]

TE_PRODUCT_ELEGIBILITY_VALUES: set[TEProductElegibility] = {
    "BpResponseAndCompliance",
    "CloudResponseStandalone",
    "DarkWeb",
    "Default",
    "Essentials",
    "MDRPromotion",
    "MSP",
}


def check_te_product_elegibility(value: str) -> TEProductElegibility:
    if value in TE_PRODUCT_ELEGIBILITY_VALUES:
        return cast(TEProductElegibility, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {TE_PRODUCT_ELEGIBILITY_VALUES!r}")
