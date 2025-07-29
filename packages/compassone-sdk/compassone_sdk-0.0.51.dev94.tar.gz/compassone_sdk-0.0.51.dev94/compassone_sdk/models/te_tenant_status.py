from typing import Literal, cast

TETenantStatus = Literal["Active", "Trial", "Unknown"]

TE_TENANT_STATUS_VALUES: set[TETenantStatus] = {
    "Active",
    "Trial",
    "Unknown",
}


def check_te_tenant_status(value: str) -> TETenantStatus:
    if value in TE_TENANT_STATUS_VALUES:
        return cast(TETenantStatus, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {TE_TENANT_STATUS_VALUES!r}")
