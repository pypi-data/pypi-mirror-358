from typing import Literal, cast

CCMs365DefensePolicyConfigExtendedAppConsentState = Literal["DISABLED", "LEGACY", "LOW"]

CC_MS_365_DEFENSE_POLICY_CONFIG_EXTENDED_APP_CONSENT_STATE_VALUES: set[
    CCMs365DefensePolicyConfigExtendedAppConsentState
] = {
    "DISABLED",
    "LEGACY",
    "LOW",
}


def check_cc_ms_365_defense_policy_config_extended_app_consent_state(
    value: str,
) -> CCMs365DefensePolicyConfigExtendedAppConsentState:
    if value in CC_MS_365_DEFENSE_POLICY_CONFIG_EXTENDED_APP_CONSENT_STATE_VALUES:
        return cast(CCMs365DefensePolicyConfigExtendedAppConsentState, value)
    raise TypeError(
        f"Unexpected value {value!r}. Expected one of {CC_MS_365_DEFENSE_POLICY_CONFIG_EXTENDED_APP_CONSENT_STATE_VALUES!r}"
    )
