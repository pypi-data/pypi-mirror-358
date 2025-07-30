from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.te_contact_group_type import TEContactGroupType, check_te_contact_group_type

if TYPE_CHECKING:
    from ..models.tev1_contact_group_member_dto import TEV1ContactGroupMemberDto


T = TypeVar("T", bound="TEV1ContactGroupWithMembersDto")


@_attrs_define
class TEV1ContactGroupWithMembersDto:
    """
    Attributes:
        type_ (TEContactGroupType):
        members (list['TEV1ContactGroupMemberDto']):
        id (str):
        name (str):
    """

    type_: TEContactGroupType
    members: list["TEV1ContactGroupMemberDto"]
    id: str
    name: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        type_: str = self.type_

        members = []
        for members_item_data in self.members:
            members_item = members_item_data.to_dict()
            members.append(members_item)

        id = self.id

        name = self.name

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "type": type_,
                "members": members,
                "id": id,
                "name": name,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.tev1_contact_group_member_dto import TEV1ContactGroupMemberDto

        d = dict(src_dict)
        type_ = check_te_contact_group_type(d.pop("type"))

        members = []
        _members = d.pop("members")
        for members_item_data in _members:
            members_item = TEV1ContactGroupMemberDto.from_dict(members_item_data)

            members.append(members_item)

        id = d.pop("id")

        name = d.pop("name")

        tev1_contact_group_with_members_dto = cls(
            type_=type_,
            members=members,
            id=id,
            name=name,
        )

        tev1_contact_group_with_members_dto.additional_properties = d
        return tev1_contact_group_with_members_dto

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
