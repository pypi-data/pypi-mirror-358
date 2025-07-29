from typing import Literal, cast

GetContactGroupControllerGetTenantsSortBy = Literal["tenant.name"]

GET_CONTACT_GROUP_CONTROLLER_GET_TENANTS_SORT_BY_VALUES: set[GetContactGroupControllerGetTenantsSortBy] = {
    "tenant.name",
}


def check_get_contact_group_controller_get_tenants_sort_by(value: str) -> GetContactGroupControllerGetTenantsSortBy:
    if value in GET_CONTACT_GROUP_CONTROLLER_GET_TENANTS_SORT_BY_VALUES:
        return cast(GetContactGroupControllerGetTenantsSortBy, value)
    raise TypeError(
        f"Unexpected value {value!r}. Expected one of {GET_CONTACT_GROUP_CONTROLLER_GET_TENANTS_SORT_BY_VALUES!r}"
    )
