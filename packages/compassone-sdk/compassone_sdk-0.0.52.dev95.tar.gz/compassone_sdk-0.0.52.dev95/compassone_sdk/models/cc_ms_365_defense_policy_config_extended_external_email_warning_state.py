from typing import Literal, cast

CCMs365DefensePolicyConfigExtendedExternalEmailWarningState = Literal["DISABLED", "ENABLED", "NON_EXISTENT"]

CC_MS_365_DEFENSE_POLICY_CONFIG_EXTENDED_EXTERNAL_EMAIL_WARNING_STATE_VALUES: set[
    CCMs365DefensePolicyConfigExtendedExternalEmailWarningState
] = {
    "DISABLED",
    "ENABLED",
    "NON_EXISTENT",
}


def check_cc_ms_365_defense_policy_config_extended_external_email_warning_state(
    value: str,
) -> CCMs365DefensePolicyConfigExtendedExternalEmailWarningState:
    if value in CC_MS_365_DEFENSE_POLICY_CONFIG_EXTENDED_EXTERNAL_EMAIL_WARNING_STATE_VALUES:
        return cast(CCMs365DefensePolicyConfigExtendedExternalEmailWarningState, value)
    raise TypeError(
        f"Unexpected value {value!r}. Expected one of {CC_MS_365_DEFENSE_POLICY_CONFIG_EXTENDED_EXTERNAL_EMAIL_WARNING_STATE_VALUES!r}"
    )
