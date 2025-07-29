from typing import Literal, cast

GetAccountControllerListPartnershipType = Literal["Direct", "MSP", "MSSP", "VAR"]

GET_ACCOUNT_CONTROLLER_LIST_PARTNERSHIP_TYPE_VALUES: set[GetAccountControllerListPartnershipType] = {
    "Direct",
    "MSP",
    "MSSP",
    "VAR",
}


def check_get_account_controller_list_partnership_type(value: str) -> GetAccountControllerListPartnershipType:
    if value in GET_ACCOUNT_CONTROLLER_LIST_PARTNERSHIP_TYPE_VALUES:
        return cast(GetAccountControllerListPartnershipType, value)
    raise TypeError(
        f"Unexpected value {value!r}. Expected one of {GET_ACCOUNT_CONTROLLER_LIST_PARTNERSHIP_TYPE_VALUES!r}"
    )
