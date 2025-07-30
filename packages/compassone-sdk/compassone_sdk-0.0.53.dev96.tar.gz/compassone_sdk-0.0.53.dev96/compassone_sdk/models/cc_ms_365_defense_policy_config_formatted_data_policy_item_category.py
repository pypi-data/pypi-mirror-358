from typing import Literal, cast

CCMs365DefensePolicyConfigFormattedDataPolicyItemCategory = Literal["Azure AD", "Exchange", "Required To Work"]

CC_MS_365_DEFENSE_POLICY_CONFIG_FORMATTED_DATA_POLICY_ITEM_CATEGORY_VALUES: set[
    CCMs365DefensePolicyConfigFormattedDataPolicyItemCategory
] = {
    "Azure AD",
    "Exchange",
    "Required To Work",
}


def check_cc_ms_365_defense_policy_config_formatted_data_policy_item_category(
    value: str,
) -> CCMs365DefensePolicyConfigFormattedDataPolicyItemCategory:
    if value in CC_MS_365_DEFENSE_POLICY_CONFIG_FORMATTED_DATA_POLICY_ITEM_CATEGORY_VALUES:
        return cast(CCMs365DefensePolicyConfigFormattedDataPolicyItemCategory, value)
    raise TypeError(
        f"Unexpected value {value!r}. Expected one of {CC_MS_365_DEFENSE_POLICY_CONFIG_FORMATTED_DATA_POLICY_ITEM_CATEGORY_VALUES!r}"
    )
