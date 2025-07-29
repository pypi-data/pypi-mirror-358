from typing import Literal, cast

TEContactGroupMemberAvailability = Literal["After Hours", "All Hours", "Business Hours"]

TE_CONTACT_GROUP_MEMBER_AVAILABILITY_VALUES: set[TEContactGroupMemberAvailability] = {
    "After Hours",
    "All Hours",
    "Business Hours",
}


def check_te_contact_group_member_availability(value: str) -> TEContactGroupMemberAvailability:
    if value in TE_CONTACT_GROUP_MEMBER_AVAILABILITY_VALUES:
        return cast(TEContactGroupMemberAvailability, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {TE_CONTACT_GROUP_MEMBER_AVAILABILITY_VALUES!r}")
