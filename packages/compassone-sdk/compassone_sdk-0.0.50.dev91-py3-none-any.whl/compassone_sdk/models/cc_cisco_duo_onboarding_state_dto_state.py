from typing import Literal, cast

CCCiscoDuoOnboardingStateDtoState = Literal[
    "complete", "Pending", "usersOnboarded", "usersOnboardedError", "usersOnboarding", "verified"
]

CC_CISCO_DUO_ONBOARDING_STATE_DTO_STATE_VALUES: set[CCCiscoDuoOnboardingStateDtoState] = {
    "complete",
    "Pending",
    "usersOnboarded",
    "usersOnboardedError",
    "usersOnboarding",
    "verified",
}


def check_cc_cisco_duo_onboarding_state_dto_state(value: str) -> CCCiscoDuoOnboardingStateDtoState:
    if value in CC_CISCO_DUO_ONBOARDING_STATE_DTO_STATE_VALUES:
        return cast(CCCiscoDuoOnboardingStateDtoState, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {CC_CISCO_DUO_ONBOARDING_STATE_DTO_STATE_VALUES!r}")
