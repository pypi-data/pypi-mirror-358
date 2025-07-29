from typing import Literal, cast

TECustomerRelationType = Literal["direct", "partner", "partner_customer", "unknown"]

TE_CUSTOMER_RELATION_TYPE_VALUES: set[TECustomerRelationType] = {
    "direct",
    "partner",
    "partner_customer",
    "unknown",
}


def check_te_customer_relation_type(value: str) -> TECustomerRelationType:
    if value in TE_CUSTOMER_RELATION_TYPE_VALUES:
        return cast(TECustomerRelationType, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {TE_CUSTOMER_RELATION_TYPE_VALUES!r}")
