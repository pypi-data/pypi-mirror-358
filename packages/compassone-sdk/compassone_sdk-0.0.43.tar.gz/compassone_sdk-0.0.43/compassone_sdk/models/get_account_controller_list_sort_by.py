from typing import Literal, cast

GetAccountControllerListSortBy = Literal["billingVersion", "created", "id", "name", "partnershipType"]

GET_ACCOUNT_CONTROLLER_LIST_SORT_BY_VALUES: set[GetAccountControllerListSortBy] = {
    "billingVersion",
    "created",
    "id",
    "name",
    "partnershipType",
}


def check_get_account_controller_list_sort_by(value: str) -> GetAccountControllerListSortBy:
    if value in GET_ACCOUNT_CONTROLLER_LIST_SORT_BY_VALUES:
        return cast(GetAccountControllerListSortBy, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {GET_ACCOUNT_CONTROLLER_LIST_SORT_BY_VALUES!r}")
