from typing import Literal, cast

CCMs365DefensePolicyConfigFormattedDataPolicyItemAlias = Literal[
    "AppConsentState",
    "AuditEnabled",
    "AutoForwardInternetEnabled",
    "ExchangeAuditAllEnabled",
    "ExternalEmailWarning",
    "MFA",
    "SafeAttachments",
    "ZapEnabled",
]

CC_MS_365_DEFENSE_POLICY_CONFIG_FORMATTED_DATA_POLICY_ITEM_ALIAS_VALUES: set[
    CCMs365DefensePolicyConfigFormattedDataPolicyItemAlias
] = {
    "AppConsentState",
    "AuditEnabled",
    "AutoForwardInternetEnabled",
    "ExchangeAuditAllEnabled",
    "ExternalEmailWarning",
    "MFA",
    "SafeAttachments",
    "ZapEnabled",
}


def check_cc_ms_365_defense_policy_config_formatted_data_policy_item_alias(
    value: str,
) -> CCMs365DefensePolicyConfigFormattedDataPolicyItemAlias:
    if value in CC_MS_365_DEFENSE_POLICY_CONFIG_FORMATTED_DATA_POLICY_ITEM_ALIAS_VALUES:
        return cast(CCMs365DefensePolicyConfigFormattedDataPolicyItemAlias, value)
    raise TypeError(
        f"Unexpected value {value!r}. Expected one of {CC_MS_365_DEFENSE_POLICY_CONFIG_FORMATTED_DATA_POLICY_ITEM_ALIAS_VALUES!r}"
    )
