from typing import Literal, cast

TEAccountBillingModel = Literal["Bulk", "Consumption"]

TE_ACCOUNT_BILLING_MODEL_VALUES: set[TEAccountBillingModel] = {
    "Bulk",
    "Consumption",
}


def check_te_account_billing_model(value: str) -> TEAccountBillingModel:
    if value in TE_ACCOUNT_BILLING_MODEL_VALUES:
        return cast(TEAccountBillingModel, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {TE_ACCOUNT_BILLING_MODEL_VALUES!r}")
