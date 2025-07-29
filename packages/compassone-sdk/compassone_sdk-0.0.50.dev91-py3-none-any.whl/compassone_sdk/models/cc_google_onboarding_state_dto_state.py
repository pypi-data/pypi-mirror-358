from typing import Literal, cast

CCGoogleOnboardingStateDtoState = Literal[
    "complete",
    "pendingConsent",
    "pendingDomainWideDelegationVerification",
    "provisionApisError",
    "provisionedApis",
    "provisionedProject",
    "provisionedRefreshToken",
    "provisionedRefreshTokenError",
    "provisionedServiceAccount",
    "provisionedServiceAccountKey",
    "provisionedServiceAccountKeyError",
    "provisionProjectError",
    "provisionServiceAccountError",
    "usersOnboarded",
    "usersOnboardedError",
    "usersOnboarding",
    "verified",
]

CC_GOOGLE_ONBOARDING_STATE_DTO_STATE_VALUES: set[CCGoogleOnboardingStateDtoState] = {
    "complete",
    "pendingConsent",
    "pendingDomainWideDelegationVerification",
    "provisionApisError",
    "provisionedApis",
    "provisionedProject",
    "provisionedRefreshToken",
    "provisionedRefreshTokenError",
    "provisionedServiceAccount",
    "provisionedServiceAccountKey",
    "provisionedServiceAccountKeyError",
    "provisionProjectError",
    "provisionServiceAccountError",
    "usersOnboarded",
    "usersOnboardedError",
    "usersOnboarding",
    "verified",
}


def check_cc_google_onboarding_state_dto_state(value: str) -> CCGoogleOnboardingStateDtoState:
    if value in CC_GOOGLE_ONBOARDING_STATE_DTO_STATE_VALUES:
        return cast(CCGoogleOnboardingStateDtoState, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {CC_GOOGLE_ONBOARDING_STATE_DTO_STATE_VALUES!r}")
