from typing import Literal, cast

TEAccountPartnershipType = Literal["Direct", "MSP", "MSSP", "VAR"]

TE_ACCOUNT_PARTNERSHIP_TYPE_VALUES: set[TEAccountPartnershipType] = {
    "Direct",
    "MSP",
    "MSSP",
    "VAR",
}


def check_te_account_partnership_type(value: str) -> TEAccountPartnershipType:
    if value in TE_ACCOUNT_PARTNERSHIP_TYPE_VALUES:
        return cast(TEAccountPartnershipType, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {TE_ACCOUNT_PARTNERSHIP_TYPE_VALUES!r}")
