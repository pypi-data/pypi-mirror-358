from typing import Literal, cast

GetTenantControllerListSortBy = Literal["created", "description", "domain", "id", "name", "type"]

GET_TENANT_CONTROLLER_LIST_SORT_BY_VALUES: set[GetTenantControllerListSortBy] = {
    "created",
    "description",
    "domain",
    "id",
    "name",
    "type",
}


def check_get_tenant_controller_list_sort_by(value: str) -> GetTenantControllerListSortBy:
    if value in GET_TENANT_CONTROLLER_LIST_SORT_BY_VALUES:
        return cast(GetTenantControllerListSortBy, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {GET_TENANT_CONTROLLER_LIST_SORT_BY_VALUES!r}")
