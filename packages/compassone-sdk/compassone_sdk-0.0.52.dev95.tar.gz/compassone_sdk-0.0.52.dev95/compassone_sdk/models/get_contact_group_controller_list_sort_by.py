from typing import Literal, cast

GetContactGroupControllerListSortBy = Literal["contactGroup.name"]

GET_CONTACT_GROUP_CONTROLLER_LIST_SORT_BY_VALUES: set[GetContactGroupControllerListSortBy] = {
    "contactGroup.name",
}


def check_get_contact_group_controller_list_sort_by(value: str) -> GetContactGroupControllerListSortBy:
    if value in GET_CONTACT_GROUP_CONTROLLER_LIST_SORT_BY_VALUES:
        return cast(GetContactGroupControllerListSortBy, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {GET_CONTACT_GROUP_CONTROLLER_LIST_SORT_BY_VALUES!r}")
