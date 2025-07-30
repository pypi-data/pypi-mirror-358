from typing import Literal, cast

TEVendorEligibleProductsAliasesItem = Literal[
    "BpResponse",
    "BpResponseAndCompliance",
    "CloudEssentials",
    "CR",
    "CrMs365",
    "DarkWeb",
    "Essentials",
    "LogIC",
    "MAC",
    "MDE",
    "MDR",
    "MDREssentials",
    "MDRPromotion",
    "Ms365Defense",
    "MSP",
    "Nicos",
    "SNAP",
    "SophosAV",
    "SophosInterceptX",
    "VulnMgmt",
    "WatchGuard",
    "WebrootAV",
]

TE_VENDOR_ELIGIBLE_PRODUCTS_ALIASES_ITEM_VALUES: set[TEVendorEligibleProductsAliasesItem] = {
    "BpResponse",
    "BpResponseAndCompliance",
    "CloudEssentials",
    "CR",
    "CrMs365",
    "DarkWeb",
    "Essentials",
    "LogIC",
    "MAC",
    "MDE",
    "MDR",
    "MDREssentials",
    "MDRPromotion",
    "Ms365Defense",
    "MSP",
    "Nicos",
    "SNAP",
    "SophosAV",
    "SophosInterceptX",
    "VulnMgmt",
    "WatchGuard",
    "WebrootAV",
}


def check_te_vendor_eligible_products_aliases_item(value: str) -> TEVendorEligibleProductsAliasesItem:
    if value in TE_VENDOR_ELIGIBLE_PRODUCTS_ALIASES_ITEM_VALUES:
        return cast(TEVendorEligibleProductsAliasesItem, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {TE_VENDOR_ELIGIBLE_PRODUCTS_ALIASES_ITEM_VALUES!r}")
