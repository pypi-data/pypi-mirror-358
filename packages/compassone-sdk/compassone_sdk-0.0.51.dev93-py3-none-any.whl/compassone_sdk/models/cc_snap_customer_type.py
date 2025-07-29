from typing import Literal, cast

CCSnapCustomerType = Literal["MDR", "MDR ONBOARD", "POC", "SELF", "UNSET"]

CC_SNAP_CUSTOMER_TYPE_VALUES: set[CCSnapCustomerType] = {
    "MDR",
    "MDR ONBOARD",
    "POC",
    "SELF",
    "UNSET",
}


def check_cc_snap_customer_type(value: str) -> CCSnapCustomerType:
    if value in CC_SNAP_CUSTOMER_TYPE_VALUES:
        return cast(CCSnapCustomerType, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {CC_SNAP_CUSTOMER_TYPE_VALUES!r}")
