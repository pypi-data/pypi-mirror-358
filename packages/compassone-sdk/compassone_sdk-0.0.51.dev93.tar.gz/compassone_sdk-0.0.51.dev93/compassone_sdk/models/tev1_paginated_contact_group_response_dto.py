from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.te_page_meta_fields_response_constraint import TEPageMetaFieldsResponseConstraint
    from ..models.tev1_contact_group_dto import TEV1ContactGroupDto


T = TypeVar("T", bound="TEV1PaginatedContactGroupResponseDto")


@_attrs_define
class TEV1PaginatedContactGroupResponseDto:
    """
    Attributes:
        data (list['TEV1ContactGroupDto']): Items returned from the database
        meta (TEPageMetaFieldsResponseConstraint):
    """

    data: list["TEV1ContactGroupDto"]
    meta: "TEPageMetaFieldsResponseConstraint"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data = []
        for data_item_data in self.data:
            data_item = data_item_data.to_dict()
            data.append(data_item)

        meta = self.meta.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "data": data,
                "meta": meta,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.te_page_meta_fields_response_constraint import TEPageMetaFieldsResponseConstraint
        from ..models.tev1_contact_group_dto import TEV1ContactGroupDto

        d = dict(src_dict)
        data = []
        _data = d.pop("data")
        for data_item_data in _data:
            data_item = TEV1ContactGroupDto.from_dict(data_item_data)

            data.append(data_item)

        meta = TEPageMetaFieldsResponseConstraint.from_dict(d.pop("meta"))

        tev1_paginated_contact_group_response_dto = cls(
            data=data,
            meta=meta,
        )

        tev1_paginated_contact_group_response_dto.additional_properties = d
        return tev1_paginated_contact_group_response_dto

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
