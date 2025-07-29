from typing import Literal, cast

TEVendorName = Literal["Arrow - ArrowSphere", "Arrow - Resell", "Blackpoint Cyber", "Pax8", "SP Partners", "Webroot"]

TE_VENDOR_NAME_VALUES: set[TEVendorName] = {
    "Arrow - ArrowSphere",
    "Arrow - Resell",
    "Blackpoint Cyber",
    "Pax8",
    "SP Partners",
    "Webroot",
}


def check_te_vendor_name(value: str) -> TEVendorName:
    if value in TE_VENDOR_NAME_VALUES:
        return cast(TEVendorName, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {TE_VENDOR_NAME_VALUES!r}")
