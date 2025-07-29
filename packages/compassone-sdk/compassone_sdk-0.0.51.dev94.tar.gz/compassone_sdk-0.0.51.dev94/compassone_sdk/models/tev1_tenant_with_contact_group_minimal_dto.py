from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.tev1_contact_group_minimal_dto import TEV1ContactGroupMinimalDto


T = TypeVar("T", bound="TEV1TenantWithContactGroupMinimalDto")


@_attrs_define
class TEV1TenantWithContactGroupMinimalDto:
    """
    Attributes:
        contact_group (TEV1ContactGroupMinimalDto):
        id (str):
        name (str):
    """

    contact_group: "TEV1ContactGroupMinimalDto"
    id: str
    name: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        contact_group = self.contact_group.to_dict()

        id = self.id

        name = self.name

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "contactGroup": contact_group,
                "id": id,
                "name": name,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.tev1_contact_group_minimal_dto import TEV1ContactGroupMinimalDto

        d = dict(src_dict)
        contact_group = TEV1ContactGroupMinimalDto.from_dict(d.pop("contactGroup"))

        id = d.pop("id")

        name = d.pop("name")

        tev1_tenant_with_contact_group_minimal_dto = cls(
            contact_group=contact_group,
            id=id,
            name=name,
        )

        tev1_tenant_with_contact_group_minimal_dto.additional_properties = d
        return tev1_tenant_with_contact_group_minimal_dto

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
