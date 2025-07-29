from typing import Literal, cast

TECustomerSourceType = Literal["CompassOne", "Legacy"]

TE_CUSTOMER_SOURCE_TYPE_VALUES: set[TECustomerSourceType] = {
    "CompassOne",
    "Legacy",
}


def check_te_customer_source_type(value: str) -> TECustomerSourceType:
    if value in TE_CUSTOMER_SOURCE_TYPE_VALUES:
        return cast(TECustomerSourceType, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {TE_CUSTOMER_SOURCE_TYPE_VALUES!r}")
