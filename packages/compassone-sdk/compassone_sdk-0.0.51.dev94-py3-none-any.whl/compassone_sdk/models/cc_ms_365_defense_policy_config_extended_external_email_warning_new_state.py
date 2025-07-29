from typing import Literal, cast

CCMs365DefensePolicyConfigExtendedExternalEmailWarningNewState = Literal[
    "DISABLED", "ENABLED", "NOT_CONFIGURED", "NOT_SUPPORTED"
]

CC_MS_365_DEFENSE_POLICY_CONFIG_EXTENDED_EXTERNAL_EMAIL_WARNING_NEW_STATE_VALUES: set[
    CCMs365DefensePolicyConfigExtendedExternalEmailWarningNewState
] = {
    "DISABLED",
    "ENABLED",
    "NOT_CONFIGURED",
    "NOT_SUPPORTED",
}


def check_cc_ms_365_defense_policy_config_extended_external_email_warning_new_state(
    value: str,
) -> CCMs365DefensePolicyConfigExtendedExternalEmailWarningNewState:
    if value in CC_MS_365_DEFENSE_POLICY_CONFIG_EXTENDED_EXTERNAL_EMAIL_WARNING_NEW_STATE_VALUES:
        return cast(CCMs365DefensePolicyConfigExtendedExternalEmailWarningNewState, value)
    raise TypeError(
        f"Unexpected value {value!r}. Expected one of {CC_MS_365_DEFENSE_POLICY_CONFIG_EXTENDED_EXTERNAL_EMAIL_WARNING_NEW_STATE_VALUES!r}"
    )
