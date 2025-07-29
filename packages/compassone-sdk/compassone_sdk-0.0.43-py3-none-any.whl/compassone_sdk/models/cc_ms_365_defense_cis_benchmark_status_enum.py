from typing import Literal, cast

CCMs365DefenseCisBenchmarkStatusEnum = Literal["Compliant", "NonCompliant", "Unknown"]

CC_MS_365_DEFENSE_CIS_BENCHMARK_STATUS_ENUM_VALUES: set[CCMs365DefenseCisBenchmarkStatusEnum] = {
    "Compliant",
    "NonCompliant",
    "Unknown",
}


def check_cc_ms_365_defense_cis_benchmark_status_enum(value: str) -> CCMs365DefenseCisBenchmarkStatusEnum:
    if value in CC_MS_365_DEFENSE_CIS_BENCHMARK_STATUS_ENUM_VALUES:
        return cast(CCMs365DefenseCisBenchmarkStatusEnum, value)
    raise TypeError(
        f"Unexpected value {value!r}. Expected one of {CC_MS_365_DEFENSE_CIS_BENCHMARK_STATUS_ENUM_VALUES!r}"
    )
