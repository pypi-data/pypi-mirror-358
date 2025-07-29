from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.cc_ms_365_defense_master_event_category import (
    CCMs365DefenseMasterEventCategory,
    check_cc_ms_365_defense_master_event_category,
)

T = TypeVar("T", bound="CCMs365DefenseMasterEvent")


@_attrs_define
class CCMs365DefenseMasterEvent:
    """
    Attributes:
        id (str):
        category (CCMs365DefenseMasterEventCategory):
        description (str):
        name (str):
    """

    id: str
    category: CCMs365DefenseMasterEventCategory
    description: str
    name: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        category: str = self.category

        description = self.description

        name = self.name

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "category": category,
                "description": description,
                "name": name,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        category = check_cc_ms_365_defense_master_event_category(d.pop("category"))

        description = d.pop("description")

        name = d.pop("name")

        cc_ms_365_defense_master_event = cls(
            id=id,
            category=category,
            description=description,
            name=name,
        )

        cc_ms_365_defense_master_event.additional_properties = d
        return cc_ms_365_defense_master_event

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
