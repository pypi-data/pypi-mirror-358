from typing import Literal, cast

GetContactGroupControllerGetUnassignedTenantsSortBy = Literal["contactGroup.name", "tenant.name"]

GET_CONTACT_GROUP_CONTROLLER_GET_UNASSIGNED_TENANTS_SORT_BY_VALUES: set[
    GetContactGroupControllerGetUnassignedTenantsSortBy
] = {
    "contactGroup.name",
    "tenant.name",
}


def check_get_contact_group_controller_get_unassigned_tenants_sort_by(
    value: str,
) -> GetContactGroupControllerGetUnassignedTenantsSortBy:
    if value in GET_CONTACT_GROUP_CONTROLLER_GET_UNASSIGNED_TENANTS_SORT_BY_VALUES:
        return cast(GetContactGroupControllerGetUnassignedTenantsSortBy, value)
    raise TypeError(
        f"Unexpected value {value!r}. Expected one of {GET_CONTACT_GROUP_CONTROLLER_GET_UNASSIGNED_TENANTS_SORT_BY_VALUES!r}"
    )
