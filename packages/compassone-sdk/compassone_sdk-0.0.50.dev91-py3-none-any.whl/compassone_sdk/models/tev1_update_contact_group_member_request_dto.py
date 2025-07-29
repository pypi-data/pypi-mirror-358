from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.te_contact_group_member_availability import (
    TEContactGroupMemberAvailability,
    check_te_contact_group_member_availability,
)

T = TypeVar("T", bound="TEV1UpdateContactGroupMemberRequestDto")


@_attrs_define
class TEV1UpdateContactGroupMemberRequestDto:
    """
    Attributes:
        availability (TEContactGroupMemberAvailability):
        name (str):
        phone_number (str):
        email (str):
        timezone (str):
        priority (float):
    """

    availability: TEContactGroupMemberAvailability
    name: str
    phone_number: str
    email: str
    timezone: str
    priority: float
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        availability: str = self.availability

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

        name = d.pop("name")

        phone_number = d.pop("phoneNumber")

        email = d.pop("email")

        timezone = d.pop("timezone")

        priority = d.pop("priority")

        tev1_update_contact_group_member_request_dto = cls(
            availability=availability,
            name=name,
            phone_number=phone_number,
            email=email,
            timezone=timezone,
            priority=priority,
        )

        tev1_update_contact_group_member_request_dto.additional_properties = d
        return tev1_update_contact_group_member_request_dto

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
