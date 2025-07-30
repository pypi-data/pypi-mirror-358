from typing import Literal, cast

TEUserPermissionType = Literal["Group", "Role"]

TE_USER_PERMISSION_TYPE_VALUES: set[TEUserPermissionType] = {
    "Group",
    "Role",
}


def check_te_user_permission_type(value: str) -> TEUserPermissionType:
    if value in TE_USER_PERMISSION_TYPE_VALUES:
        return cast(TEUserPermissionType, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {TE_USER_PERMISSION_TYPE_VALUES!r}")
