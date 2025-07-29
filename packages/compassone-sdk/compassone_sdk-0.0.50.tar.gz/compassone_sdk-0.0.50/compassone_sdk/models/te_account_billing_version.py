from typing import Literal, cast

TEAccountBillingVersion = Literal["1", "2"]

TE_ACCOUNT_BILLING_VERSION_VALUES: set[TEAccountBillingVersion] = {
    "1",
    "2",
}


def check_te_account_billing_version(value: str) -> TEAccountBillingVersion:
    if value in TE_ACCOUNT_BILLING_VERSION_VALUES:
        return cast(TEAccountBillingVersion, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {TE_ACCOUNT_BILLING_VERSION_VALUES!r}")
