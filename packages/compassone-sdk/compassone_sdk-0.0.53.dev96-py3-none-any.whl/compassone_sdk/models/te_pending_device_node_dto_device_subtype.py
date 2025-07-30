from typing import Literal, cast

TEPendingDeviceNodeDtoDeviceSubtype = Literal[
    "ACCESS_POINT",
    "CAMERA",
    "DESKTOP",
    "DOMAIN_CONTROLLER",
    "FAX",
    "FIREWALL",
    "HUB",
    "LAPTOP",
    "PHONE",
    "PRINTER",
    "ROUTER",
    "SERVER",
    "SWITCH",
    "TABLET",
    "UNKNOWN",
]

TE_PENDING_DEVICE_NODE_DTO_DEVICE_SUBTYPE_VALUES: set[TEPendingDeviceNodeDtoDeviceSubtype] = {
    "ACCESS_POINT",
    "CAMERA",
    "DESKTOP",
    "DOMAIN_CONTROLLER",
    "FAX",
    "FIREWALL",
    "HUB",
    "LAPTOP",
    "PHONE",
    "PRINTER",
    "ROUTER",
    "SERVER",
    "SWITCH",
    "TABLET",
    "UNKNOWN",
}


def check_te_pending_device_node_dto_device_subtype(value: str) -> TEPendingDeviceNodeDtoDeviceSubtype:
    if value in TE_PENDING_DEVICE_NODE_DTO_DEVICE_SUBTYPE_VALUES:
        return cast(TEPendingDeviceNodeDtoDeviceSubtype, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {TE_PENDING_DEVICE_NODE_DTO_DEVICE_SUBTYPE_VALUES!r}")
