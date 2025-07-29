from typing import Literal, cast

TEContactGroupType = Literal["Informational", "Urgent", "Urgent & Informational"]

TE_CONTACT_GROUP_TYPE_VALUES: set[TEContactGroupType] = {
    "Informational",
    "Urgent",
    "Urgent & Informational",
}


def check_te_contact_group_type(value: str) -> TEContactGroupType:
    if value in TE_CONTACT_GROUP_TYPE_VALUES:
        return cast(TEContactGroupType, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {TE_CONTACT_GROUP_TYPE_VALUES!r}")
