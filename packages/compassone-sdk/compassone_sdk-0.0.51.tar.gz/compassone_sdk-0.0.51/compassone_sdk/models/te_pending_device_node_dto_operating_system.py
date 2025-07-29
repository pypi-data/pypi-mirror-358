from typing import Literal, cast

TEPendingDeviceNodeDtoOperatingSystem = Literal[
    "ALCATEL_SROS",
    "ALCATEL_TIMOS",
    "ANDROID",
    "APPLE_IOS",
    "ARISTA_EOS",
    "BSD",
    "CAMERA_GROUP",
    "CHROMIUM",
    "CISCO_ASA",
    "CISCO_CATOS",
    "CISCO_IOS",
    "CISCO_MERAKI",
    "CISCO_PIX",
    "ENTERASYS_EOS",
    "EXTREME_XOS",
    "HUAWEI_VRP",
    "IOSXR",
    "JUNIPER_SCREENOS",
    "JUNOS",
    "LINUX",
    "MIKROTIK_ROUTEROS",
    "MIKROTIK_SWITCHOS",
    "NXOS",
    "OSX",
    "PRINTER_GROUP",
    "SOLARIS",
    "UNIX",
    "UNKNOWN",
    "WINDOWS",
    "ZXR",
]

TE_PENDING_DEVICE_NODE_DTO_OPERATING_SYSTEM_VALUES: set[TEPendingDeviceNodeDtoOperatingSystem] = {
    "ALCATEL_SROS",
    "ALCATEL_TIMOS",
    "ANDROID",
    "APPLE_IOS",
    "ARISTA_EOS",
    "BSD",
    "CAMERA_GROUP",
    "CHROMIUM",
    "CISCO_ASA",
    "CISCO_CATOS",
    "CISCO_IOS",
    "CISCO_MERAKI",
    "CISCO_PIX",
    "ENTERASYS_EOS",
    "EXTREME_XOS",
    "HUAWEI_VRP",
    "IOSXR",
    "JUNIPER_SCREENOS",
    "JUNOS",
    "LINUX",
    "MIKROTIK_ROUTEROS",
    "MIKROTIK_SWITCHOS",
    "NXOS",
    "OSX",
    "PRINTER_GROUP",
    "SOLARIS",
    "UNIX",
    "UNKNOWN",
    "WINDOWS",
    "ZXR",
}


def check_te_pending_device_node_dto_operating_system(value: str) -> TEPendingDeviceNodeDtoOperatingSystem:
    if value in TE_PENDING_DEVICE_NODE_DTO_OPERATING_SYSTEM_VALUES:
        return cast(TEPendingDeviceNodeDtoOperatingSystem, value)
    raise TypeError(
        f"Unexpected value {value!r}. Expected one of {TE_PENDING_DEVICE_NODE_DTO_OPERATING_SYSTEM_VALUES!r}"
    )
