from typing import Literal, cast

GetContactGroupControllerGetMembers2SortBy = Literal["priority"]

GET_CONTACT_GROUP_CONTROLLER_GET_MEMBERS_2_SORT_BY_VALUES: set[GetContactGroupControllerGetMembers2SortBy] = {
    "priority",
}


def check_get_contact_group_controller_get_members_2_sort_by(value: str) -> GetContactGroupControllerGetMembers2SortBy:
    if value in GET_CONTACT_GROUP_CONTROLLER_GET_MEMBERS_2_SORT_BY_VALUES:
        return cast(GetContactGroupControllerGetMembers2SortBy, value)
    raise TypeError(
        f"Unexpected value {value!r}. Expected one of {GET_CONTACT_GROUP_CONTROLLER_GET_MEMBERS_2_SORT_BY_VALUES!r}"
    )
