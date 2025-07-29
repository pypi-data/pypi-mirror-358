from typing import Literal, cast

TEVendorType = Literal["Default", "ProductVendor"]

TE_VENDOR_TYPE_VALUES: set[TEVendorType] = {
    "Default",
    "ProductVendor",
}


def check_te_vendor_type(value: str) -> TEVendorType:
    if value in TE_VENDOR_TYPE_VALUES:
        return cast(TEVendorType, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {TE_VENDOR_TYPE_VALUES!r}")
