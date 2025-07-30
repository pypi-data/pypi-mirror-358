from typing import Literal, cast

GetListM365UsersOrderBy = Literal["email", "enabled", "licensed"]

GET_LIST_M365_USERS_ORDER_BY_VALUES: set[GetListM365UsersOrderBy] = {
    "email",
    "enabled",
    "licensed",
}


def check_get_list_m365_users_order_by(value: str) -> GetListM365UsersOrderBy:
    if value in GET_LIST_M365_USERS_ORDER_BY_VALUES:
        return cast(GetListM365UsersOrderBy, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {GET_LIST_M365_USERS_ORDER_BY_VALUES!r}")
