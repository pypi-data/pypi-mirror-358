from typing import Literal, cast

CCMs365DefensePackageOnboardingStage = Literal[
    "S1ValidatePrimaryDomain",
    "S2GrantPermissionsToApp",
    "S3ValidateGlobalAdminRole",
    "S4EnableAuditing",
    "S5RegisterWebhooks",
    "S6bConfiguringGroups",
    "S6CompleteOnboarding",
    "S7Completed",
]

CC_MS_365_DEFENSE_PACKAGE_ONBOARDING_STAGE_VALUES: set[CCMs365DefensePackageOnboardingStage] = {
    "S1ValidatePrimaryDomain",
    "S2GrantPermissionsToApp",
    "S3ValidateGlobalAdminRole",
    "S4EnableAuditing",
    "S5RegisterWebhooks",
    "S6bConfiguringGroups",
    "S6CompleteOnboarding",
    "S7Completed",
}


def check_cc_ms_365_defense_package_onboarding_stage(value: str) -> CCMs365DefensePackageOnboardingStage:
    if value in CC_MS_365_DEFENSE_PACKAGE_ONBOARDING_STAGE_VALUES:
        return cast(CCMs365DefensePackageOnboardingStage, value)
    raise TypeError(
        f"Unexpected value {value!r}. Expected one of {CC_MS_365_DEFENSE_PACKAGE_ONBOARDING_STAGE_VALUES!r}"
    )
