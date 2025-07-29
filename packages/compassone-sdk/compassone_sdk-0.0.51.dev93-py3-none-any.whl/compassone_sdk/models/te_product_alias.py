from typing import Literal, cast

TEProductAlias = Literal[
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

TE_PRODUCT_ALIAS_VALUES: set[TEProductAlias] = {
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


def check_te_product_alias(value: str) -> TEProductAlias:
    if value in TE_PRODUCT_ALIAS_VALUES:
        return cast(TEProductAlias, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {TE_PRODUCT_ALIAS_VALUES!r}")
