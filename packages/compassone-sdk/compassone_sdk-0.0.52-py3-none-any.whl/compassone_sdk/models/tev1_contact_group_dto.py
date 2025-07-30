import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.te_contact_group_type import TEContactGroupType, check_te_contact_group_type

if TYPE_CHECKING:
    from ..models.tev1_contact_group_member_dto import TEV1ContactGroupMemberDto
    from ..models.tev1_contact_group_tenant_minimal_dto import TEV1ContactGroupTenantMinimalDto


T = TypeVar("T", bound="TEV1ContactGroupDto")


@_attrs_define
class TEV1ContactGroupDto:
    """
    Attributes:
        type_ (TEContactGroupType):
        total_members (float):
        total_assigned_tenants (float):
        members (list['TEV1ContactGroupMemberDto']):
        assigned_tenants (list['TEV1ContactGroupTenantMinimalDto']):
        id (str):
        name (str):
        created (datetime.datetime):
    """

    type_: TEContactGroupType
    total_members: float
    total_assigned_tenants: float
    members: list["TEV1ContactGroupMemberDto"]
    assigned_tenants: list["TEV1ContactGroupTenantMinimalDto"]
    id: str
    name: str
    created: datetime.datetime
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        type_: str = self.type_

        total_members = self.total_members

        total_assigned_tenants = self.total_assigned_tenants

        members = []
        for members_item_data in self.members:
            members_item = members_item_data.to_dict()
            members.append(members_item)

        assigned_tenants = []
        for assigned_tenants_item_data in self.assigned_tenants:
            assigned_tenants_item = assigned_tenants_item_data.to_dict()
            assigned_tenants.append(assigned_tenants_item)

        id = self.id

        name = self.name

        created = self.created.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "type": type_,
                "totalMembers": total_members,
                "totalAssignedTenants": total_assigned_tenants,
                "members": members,
                "assignedTenants": assigned_tenants,
                "id": id,
                "name": name,
                "created": created,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.tev1_contact_group_member_dto import TEV1ContactGroupMemberDto
        from ..models.tev1_contact_group_tenant_minimal_dto import TEV1ContactGroupTenantMinimalDto

        d = dict(src_dict)
        type_ = check_te_contact_group_type(d.pop("type"))

        total_members = d.pop("totalMembers")

        total_assigned_tenants = d.pop("totalAssignedTenants")

        members = []
        _members = d.pop("members")
        for members_item_data in _members:
            members_item = TEV1ContactGroupMemberDto.from_dict(members_item_data)

            members.append(members_item)

        assigned_tenants = []
        _assigned_tenants = d.pop("assignedTenants")
        for assigned_tenants_item_data in _assigned_tenants:
            assigned_tenants_item = TEV1ContactGroupTenantMinimalDto.from_dict(assigned_tenants_item_data)

            assigned_tenants.append(assigned_tenants_item)

        id = d.pop("id")

        name = d.pop("name")

        created = isoparse(d.pop("created"))

        tev1_contact_group_dto = cls(
            type_=type_,
            total_members=total_members,
            total_assigned_tenants=total_assigned_tenants,
            members=members,
            assigned_tenants=assigned_tenants,
            id=id,
            name=name,
            created=created,
        )

        tev1_contact_group_dto.additional_properties = d
        return tev1_contact_group_dto

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
