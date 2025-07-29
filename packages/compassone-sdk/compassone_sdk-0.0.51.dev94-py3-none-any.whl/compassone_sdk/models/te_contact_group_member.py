import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.te_contact_group_member_availability import (
    TEContactGroupMemberAvailability,
    check_te_contact_group_member_availability,
)
from ..types import UNSET, Unset

T = TypeVar("T", bound="TEContactGroupMember")


@_attrs_define
class TEContactGroupMember:
    """
    Attributes:
        availability (TEContactGroupMemberAvailability):
        id (str):
        contact_group_id (str):
        name (str):
        phone_number (str):
        email (str):
        timezone (str):
        priority (float):
        created (datetime.datetime):
        updated (Union[None, Unset, datetime.datetime]):
        deleted (Union[None, Unset, datetime.datetime]):
    """

    availability: TEContactGroupMemberAvailability
    id: str
    contact_group_id: str
    name: str
    phone_number: str
    email: str
    timezone: str
    priority: float
    created: datetime.datetime
    updated: Union[None, Unset, datetime.datetime] = UNSET
    deleted: Union[None, Unset, datetime.datetime] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        availability: str = self.availability

        id = self.id

        contact_group_id = self.contact_group_id

        name = self.name

        phone_number = self.phone_number

        email = self.email

        timezone = self.timezone

        priority = self.priority

        created = self.created.isoformat()

        updated: Union[None, Unset, str]
        if isinstance(self.updated, Unset):
            updated = UNSET
        elif isinstance(self.updated, datetime.datetime):
            updated = self.updated.isoformat()
        else:
            updated = self.updated

        deleted: Union[None, Unset, str]
        if isinstance(self.deleted, Unset):
            deleted = UNSET
        elif isinstance(self.deleted, datetime.datetime):
            deleted = self.deleted.isoformat()
        else:
            deleted = self.deleted

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "availability": availability,
                "id": id,
                "contactGroupId": contact_group_id,
                "name": name,
                "phoneNumber": phone_number,
                "email": email,
                "timezone": timezone,
                "priority": priority,
                "created": created,
            }
        )
        if updated is not UNSET:
            field_dict["updated"] = updated
        if deleted is not UNSET:
            field_dict["deleted"] = deleted

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        availability = check_te_contact_group_member_availability(d.pop("availability"))

        id = d.pop("id")

        contact_group_id = d.pop("contactGroupId")

        name = d.pop("name")

        phone_number = d.pop("phoneNumber")

        email = d.pop("email")

        timezone = d.pop("timezone")

        priority = d.pop("priority")

        created = isoparse(d.pop("created"))

        def _parse_updated(data: object) -> Union[None, Unset, datetime.datetime]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                updated_type_0 = isoparse(data)

                return updated_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, datetime.datetime], data)

        updated = _parse_updated(d.pop("updated", UNSET))

        def _parse_deleted(data: object) -> Union[None, Unset, datetime.datetime]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                deleted_type_0 = isoparse(data)

                return deleted_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, datetime.datetime], data)

        deleted = _parse_deleted(d.pop("deleted", UNSET))

        te_contact_group_member = cls(
            availability=availability,
            id=id,
            contact_group_id=contact_group_id,
            name=name,
            phone_number=phone_number,
            email=email,
            timezone=timezone,
            priority=priority,
            created=created,
            updated=updated,
            deleted=deleted,
        )

        te_contact_group_member.additional_properties = d
        return te_contact_group_member

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
