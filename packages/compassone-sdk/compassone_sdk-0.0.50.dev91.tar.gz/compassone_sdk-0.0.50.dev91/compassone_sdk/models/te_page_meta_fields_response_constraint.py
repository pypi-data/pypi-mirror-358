from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="TEPageMetaFieldsResponseConstraint")


@_attrs_define
class TEPageMetaFieldsResponseConstraint:
    """
    Attributes:
        current_page (float):
        total_items (float):
        total_pages (float):
        page_size (float):
    """

    current_page: float
    total_items: float
    total_pages: float
    page_size: float
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        current_page = self.current_page

        total_items = self.total_items

        total_pages = self.total_pages

        page_size = self.page_size

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "currentPage": current_page,
                "totalItems": total_items,
                "totalPages": total_pages,
                "pageSize": page_size,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        current_page = d.pop("currentPage")

        total_items = d.pop("totalItems")

        total_pages = d.pop("totalPages")

        page_size = d.pop("pageSize")

        te_page_meta_fields_response_constraint = cls(
            current_page=current_page,
            total_items=total_items,
            total_pages=total_pages,
            page_size=page_size,
        )

        te_page_meta_fields_response_constraint.additional_properties = d
        return te_page_meta_fields_response_constraint

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
