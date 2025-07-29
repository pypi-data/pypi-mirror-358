from typing import Literal, cast

CCMs365DefenseCisBenchmarkStatus = Literal["Compliant", "NonCompliant", "Unknown"]

CC_MS_365_DEFENSE_CIS_BENCHMARK_STATUS_VALUES: set[CCMs365DefenseCisBenchmarkStatus] = {
    "Compliant",
    "NonCompliant",
    "Unknown",
}


def check_cc_ms_365_defense_cis_benchmark_status(value: str) -> CCMs365DefenseCisBenchmarkStatus:
    if value in CC_MS_365_DEFENSE_CIS_BENCHMARK_STATUS_VALUES:
        return cast(CCMs365DefenseCisBenchmarkStatus, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {CC_MS_365_DEFENSE_CIS_BENCHMARK_STATUS_VALUES!r}")
