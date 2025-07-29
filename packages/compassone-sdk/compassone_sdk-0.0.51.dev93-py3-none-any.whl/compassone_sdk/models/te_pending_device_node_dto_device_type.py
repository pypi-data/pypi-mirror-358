from typing import Literal, cast

TEPendingDeviceNodeDtoDeviceType = Literal["ENDHOST", "MOBILE", "NETWORK", "OFFICE", "SERVER", "UNKNOWN"]

TE_PENDING_DEVICE_NODE_DTO_DEVICE_TYPE_VALUES: set[TEPendingDeviceNodeDtoDeviceType] = {
    "ENDHOST",
    "MOBILE",
    "NETWORK",
    "OFFICE",
    "SERVER",
    "UNKNOWN",
}


def check_te_pending_device_node_dto_device_type(value: str) -> TEPendingDeviceNodeDtoDeviceType:
    if value in TE_PENDING_DEVICE_NODE_DTO_DEVICE_TYPE_VALUES:
        return cast(TEPendingDeviceNodeDtoDeviceType, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {TE_PENDING_DEVICE_NODE_DTO_DEVICE_TYPE_VALUES!r}")
