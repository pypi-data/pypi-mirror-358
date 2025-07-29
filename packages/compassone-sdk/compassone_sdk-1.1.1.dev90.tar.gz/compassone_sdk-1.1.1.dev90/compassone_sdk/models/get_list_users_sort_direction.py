from typing import Literal, cast

GetListUsersSortDirection = Literal["ASC", "DESC"]

GET_LIST_USERS_SORT_DIRECTION_VALUES: set[GetListUsersSortDirection] = {
    "ASC",
    "DESC",
}


def check_get_list_users_sort_direction(value: str) -> GetListUsersSortDirection:
    if value in GET_LIST_USERS_SORT_DIRECTION_VALUES:
        return cast(GetListUsersSortDirection, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {GET_LIST_USERS_SORT_DIRECTION_VALUES!r}")
