import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.te_invite_type import TEInviteType, check_te_invite_type
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.te_user import TEUser


T = TypeVar("T", bound="TEInvite")


@_attrs_define
class TEInvite:
    """
    Attributes:
        type_ (TEInviteType):
        id (str):
        sender_id (str):
        recipient_id (str):
        created (datetime.datetime):
        sender (Union[Unset, TEUser]):
        recipient (Union[Unset, TEUser]):
        accepted_on (Union[None, Unset, datetime.datetime]):
        account_id (Union[None, Unset, str]):
        updated (Union[None, Unset, datetime.datetime]):
        deleted (Union[None, Unset, datetime.datetime]):
    """

    type_: TEInviteType
    id: str
    sender_id: str
    recipient_id: str
    created: datetime.datetime
    sender: Union[Unset, "TEUser"] = UNSET
    recipient: Union[Unset, "TEUser"] = UNSET
    accepted_on: Union[None, Unset, datetime.datetime] = UNSET
    account_id: Union[None, Unset, str] = UNSET
    updated: Union[None, Unset, datetime.datetime] = UNSET
    deleted: Union[None, Unset, datetime.datetime] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        type_: str = self.type_

        id = self.id

        sender_id = self.sender_id

        recipient_id = self.recipient_id

        created = self.created.isoformat()

        sender: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.sender, Unset):
            sender = self.sender.to_dict()

        recipient: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.recipient, Unset):
            recipient = self.recipient.to_dict()

        accepted_on: Union[None, Unset, str]
        if isinstance(self.accepted_on, Unset):
            accepted_on = UNSET
        elif isinstance(self.accepted_on, datetime.datetime):
            accepted_on = self.accepted_on.isoformat()
        else:
            accepted_on = self.accepted_on

        account_id: Union[None, Unset, str]
        if isinstance(self.account_id, Unset):
            account_id = UNSET
        else:
            account_id = self.account_id

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
                "type": type_,
                "id": id,
                "senderId": sender_id,
                "recipientId": recipient_id,
                "created": created,
            }
        )
        if sender is not UNSET:
            field_dict["sender"] = sender
        if recipient is not UNSET:
            field_dict["recipient"] = recipient
        if accepted_on is not UNSET:
            field_dict["acceptedOn"] = accepted_on
        if account_id is not UNSET:
            field_dict["accountId"] = account_id
        if updated is not UNSET:
            field_dict["updated"] = updated
        if deleted is not UNSET:
            field_dict["deleted"] = deleted

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.te_user import TEUser

        d = dict(src_dict)
        type_ = check_te_invite_type(d.pop("type"))

        id = d.pop("id")

        sender_id = d.pop("senderId")

        recipient_id = d.pop("recipientId")

        created = isoparse(d.pop("created"))

        _sender = d.pop("sender", UNSET)
        sender: Union[Unset, TEUser]
        if isinstance(_sender, Unset):
            sender = UNSET
        else:
            sender = TEUser.from_dict(_sender)

        _recipient = d.pop("recipient", UNSET)
        recipient: Union[Unset, TEUser]
        if isinstance(_recipient, Unset):
            recipient = UNSET
        else:
            recipient = TEUser.from_dict(_recipient)

        def _parse_accepted_on(data: object) -> Union[None, Unset, datetime.datetime]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                accepted_on_type_0 = isoparse(data)

                return accepted_on_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, datetime.datetime], data)

        accepted_on = _parse_accepted_on(d.pop("acceptedOn", UNSET))

        def _parse_account_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        account_id = _parse_account_id(d.pop("accountId", UNSET))

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

        te_invite = cls(
            type_=type_,
            id=id,
            sender_id=sender_id,
            recipient_id=recipient_id,
            created=created,
            sender=sender,
            recipient=recipient,
            accepted_on=accepted_on,
            account_id=account_id,
            updated=updated,
            deleted=deleted,
        )

        te_invite.additional_properties = d
        return te_invite

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
