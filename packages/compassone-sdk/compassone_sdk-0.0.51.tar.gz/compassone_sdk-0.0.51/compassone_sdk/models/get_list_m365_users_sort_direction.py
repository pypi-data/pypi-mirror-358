from typing import Literal, cast

GetListM365UsersSortDirection = Literal["ASC", "DESC"]

GET_LIST_M365_USERS_SORT_DIRECTION_VALUES: set[GetListM365UsersSortDirection] = {
    "ASC",
    "DESC",
}


def check_get_list_m365_users_sort_direction(value: str) -> GetListM365UsersSortDirection:
    if value in GET_LIST_M365_USERS_SORT_DIRECTION_VALUES:
        return cast(GetListM365UsersSortDirection, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {GET_LIST_M365_USERS_SORT_DIRECTION_VALUES!r}")
