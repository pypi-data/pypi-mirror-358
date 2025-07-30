from typing import Literal, cast

TEInviteType = Literal["AccountInvite", "UserInvite"]

TE_INVITE_TYPE_VALUES: set[TEInviteType] = {
    "AccountInvite",
    "UserInvite",
}


def check_te_invite_type(value: str) -> TEInviteType:
    if value in TE_INVITE_TYPE_VALUES:
        return cast(TEInviteType, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {TE_INVITE_TYPE_VALUES!r}")
