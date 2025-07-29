from typing import Literal, cast

TESnapCustomerType = Literal["MDR", "MDR ONBOARD", "POC", "SELF", "UNSET"]

TE_SNAP_CUSTOMER_TYPE_VALUES: set[TESnapCustomerType] = {
    "MDR",
    "MDR ONBOARD",
    "POC",
    "SELF",
    "UNSET",
}


def check_te_snap_customer_type(value: str) -> TESnapCustomerType:
    if value in TE_SNAP_CUSTOMER_TYPE_VALUES:
        return cast(TESnapCustomerType, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {TE_SNAP_CUSTOMER_TYPE_VALUES!r}")
