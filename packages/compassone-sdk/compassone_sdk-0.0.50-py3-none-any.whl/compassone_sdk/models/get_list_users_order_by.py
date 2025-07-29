from typing import Literal, cast

GetListUsersOrderBy = Literal["email", "name"]

GET_LIST_USERS_ORDER_BY_VALUES: set[GetListUsersOrderBy] = {
    "email",
    "name",
}


def check_get_list_users_order_by(value: str) -> GetListUsersOrderBy:
    if value in GET_LIST_USERS_ORDER_BY_VALUES:
        return cast(GetListUsersOrderBy, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {GET_LIST_USERS_ORDER_BY_VALUES!r}")
