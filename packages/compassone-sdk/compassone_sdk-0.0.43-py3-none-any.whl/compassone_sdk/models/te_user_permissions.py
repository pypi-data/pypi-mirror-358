from typing import Literal, cast

TEUserPermissions = Literal[
    "AccountAdmin",
    "AccountBillingAbility",
    "AccountUser",
    "BlackpointAdmin",
    "BlackpointSuperAdmin",
    "BlackpointUser",
    "CustomerAdmin",
    "CustomerUser",
    "Portal",
    "Snap",
]

TE_USER_PERMISSIONS_VALUES: set[TEUserPermissions] = {
    "AccountAdmin",
    "AccountBillingAbility",
    "AccountUser",
    "BlackpointAdmin",
    "BlackpointSuperAdmin",
    "BlackpointUser",
    "CustomerAdmin",
    "CustomerUser",
    "Portal",
    "Snap",
}


def check_te_user_permissions(value: str) -> TEUserPermissions:
    if value in TE_USER_PERMISSIONS_VALUES:
        return cast(TEUserPermissions, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {TE_USER_PERMISSIONS_VALUES!r}")
