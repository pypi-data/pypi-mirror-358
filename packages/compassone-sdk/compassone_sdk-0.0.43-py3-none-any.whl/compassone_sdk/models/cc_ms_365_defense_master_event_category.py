from typing import Literal, cast

CCMs365DefenseMasterEventCategory = Literal["Azure AD", "Exchange", "SharePoint"]

CC_MS_365_DEFENSE_MASTER_EVENT_CATEGORY_VALUES: set[CCMs365DefenseMasterEventCategory] = {
    "Azure AD",
    "Exchange",
    "SharePoint",
}


def check_cc_ms_365_defense_master_event_category(value: str) -> CCMs365DefenseMasterEventCategory:
    if value in CC_MS_365_DEFENSE_MASTER_EVENT_CATEGORY_VALUES:
        return cast(CCMs365DefenseMasterEventCategory, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {CC_MS_365_DEFENSE_MASTER_EVENT_CATEGORY_VALUES!r}")
