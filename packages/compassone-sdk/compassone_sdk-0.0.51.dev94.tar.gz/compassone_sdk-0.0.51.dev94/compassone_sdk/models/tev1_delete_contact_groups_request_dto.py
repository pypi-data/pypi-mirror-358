from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="TEV1DeleteContactGroupsRequestDto")


@_attrs_define
class TEV1DeleteContactGroupsRequestDto:
    """
    Attributes:
        contact_group_ids (list[str]):
    """

    contact_group_ids: list[str]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        contact_group_ids = self.contact_group_ids

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "contactGroupIds": contact_group_ids,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        contact_group_ids = cast(list[str], d.pop("contactGroupIds"))

        tev1_delete_contact_groups_request_dto = cls(
            contact_group_ids=contact_group_ids,
        )

        tev1_delete_contact_groups_request_dto.additional_properties = d
        return tev1_delete_contact_groups_request_dto

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
