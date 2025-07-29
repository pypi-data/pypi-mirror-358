from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.te_contact_group_member_availability import (
    TEContactGroupMemberAvailability,
    check_te_contact_group_member_availability,
)

T = TypeVar("T", bound="TEV1ContactGroupMemberDto")


@_attrs_define
class TEV1ContactGroupMemberDto:
    """
    Attributes:
        availability (TEContactGroupMemberAvailability):
        id (str):
        name (str):
        phone_number (str):
        email (str):
        timezone (str):
        priority (float):
    """

    availability: TEContactGroupMemberAvailability
    id: str
    name: str
    phone_number: str
    email: str
    timezone: str
    priority: float
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        availability: str = self.availability

        id = self.id

        name = self.name

        phone_number = self.phone_number

        email = self.email

        timezone = self.timezone

        priority = self.priority

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "availability": availability,
                "id": id,
                "name": name,
                "phoneNumber": phone_number,
                "email": email,
                "timezone": timezone,
                "priority": priority,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        availability = check_te_contact_group_member_availability(d.pop("availability"))

        id = d.pop("id")

        name = d.pop("name")

        phone_number = d.pop("phoneNumber")

        email = d.pop("email")

        timezone = d.pop("timezone")

        priority = d.pop("priority")

        tev1_contact_group_member_dto = cls(
            availability=availability,
            id=id,
            name=name,
            phone_number=phone_number,
            email=email,
            timezone=timezone,
            priority=priority,
        )

        tev1_contact_group_member_dto.additional_properties = d
        return tev1_contact_group_member_dto

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
