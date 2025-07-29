from typing import Literal, cast

CCMs365DefensePolicyConfigExtendedSafeAttachmentsAction = Literal["ALLOW", "BLOCK", "DYNAMIC_DELIVERY", "REPLACE"]

CC_MS_365_DEFENSE_POLICY_CONFIG_EXTENDED_SAFE_ATTACHMENTS_ACTION_VALUES: set[
    CCMs365DefensePolicyConfigExtendedSafeAttachmentsAction
] = {
    "ALLOW",
    "BLOCK",
    "DYNAMIC_DELIVERY",
    "REPLACE",
}


def check_cc_ms_365_defense_policy_config_extended_safe_attachments_action(
    value: str,
) -> CCMs365DefensePolicyConfigExtendedSafeAttachmentsAction:
    if value in CC_MS_365_DEFENSE_POLICY_CONFIG_EXTENDED_SAFE_ATTACHMENTS_ACTION_VALUES:
        return cast(CCMs365DefensePolicyConfigExtendedSafeAttachmentsAction, value)
    raise TypeError(
        f"Unexpected value {value!r}. Expected one of {CC_MS_365_DEFENSE_POLICY_CONFIG_EXTENDED_SAFE_ATTACHMENTS_ACTION_VALUES!r}"
    )
