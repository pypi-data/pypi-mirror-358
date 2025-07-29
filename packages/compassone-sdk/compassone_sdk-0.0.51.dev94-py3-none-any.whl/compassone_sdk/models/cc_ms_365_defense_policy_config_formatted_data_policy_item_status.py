from typing import Literal, cast

CCMs365DefensePolicyConfigFormattedDataPolicyItemStatus = Literal["Error", "Secured", "Warning"]

CC_MS_365_DEFENSE_POLICY_CONFIG_FORMATTED_DATA_POLICY_ITEM_STATUS_VALUES: set[
    CCMs365DefensePolicyConfigFormattedDataPolicyItemStatus
] = {
    "Error",
    "Secured",
    "Warning",
}


def check_cc_ms_365_defense_policy_config_formatted_data_policy_item_status(
    value: str,
) -> CCMs365DefensePolicyConfigFormattedDataPolicyItemStatus:
    if value in CC_MS_365_DEFENSE_POLICY_CONFIG_FORMATTED_DATA_POLICY_ITEM_STATUS_VALUES:
        return cast(CCMs365DefensePolicyConfigFormattedDataPolicyItemStatus, value)
    raise TypeError(
        f"Unexpected value {value!r}. Expected one of {CC_MS_365_DEFENSE_POLICY_CONFIG_FORMATTED_DATA_POLICY_ITEM_STATUS_VALUES!r}"
    )
