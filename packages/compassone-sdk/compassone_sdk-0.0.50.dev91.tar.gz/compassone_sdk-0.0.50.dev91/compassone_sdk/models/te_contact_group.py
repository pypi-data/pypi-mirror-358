import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.te_contact_group_type import TEContactGroupType, check_te_contact_group_type
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.te_contact_group_member import TEContactGroupMember
    from ..models.te_customer import TECustomer


T = TypeVar("T", bound="TEContactGroup")


@_attrs_define
class TEContactGroup:
    """
    Attributes:
        type_ (TEContactGroupType):
        id (str):
        name (str):
        account_id (str):
        created (datetime.datetime):
        members (Union[Unset, list['TEContactGroupMember']]):
        assigned_customers (Union[None, Unset, list['TECustomer']]):
        updated (Union[None, Unset, datetime.datetime]):
        deleted (Union[None, Unset, datetime.datetime]):
    """

    type_: TEContactGroupType
    id: str
    name: str
    account_id: str
    created: datetime.datetime
    members: Union[Unset, list["TEContactGroupMember"]] = UNSET
    assigned_customers: Union[None, Unset, list["TECustomer"]] = UNSET
    updated: Union[None, Unset, datetime.datetime] = UNSET
    deleted: Union[None, Unset, datetime.datetime] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        type_: str = self.type_

        id = self.id

        name = self.name

        account_id = self.account_id

        created = self.created.isoformat()

        members: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.members, Unset):
            members = []
            for members_item_data in self.members:
                members_item = members_item_data.to_dict()
                members.append(members_item)

        assigned_customers: Union[None, Unset, list[dict[str, Any]]]
        if isinstance(self.assigned_customers, Unset):
            assigned_customers = UNSET
        elif isinstance(self.assigned_customers, list):
            assigned_customers = []
            for assigned_customers_type_0_item_data in self.assigned_customers:
                assigned_customers_type_0_item = assigned_customers_type_0_item_data.to_dict()
                assigned_customers.append(assigned_customers_type_0_item)

        else:
            assigned_customers = self.assigned_customers

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
                "name": name,
                "accountId": account_id,
                "created": created,
            }
        )
        if members is not UNSET:
            field_dict["members"] = members
        if assigned_customers is not UNSET:
            field_dict["assignedCustomers"] = assigned_customers
        if updated is not UNSET:
            field_dict["updated"] = updated
        if deleted is not UNSET:
            field_dict["deleted"] = deleted

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.te_contact_group_member import TEContactGroupMember
        from ..models.te_customer import TECustomer

        d = dict(src_dict)
        type_ = check_te_contact_group_type(d.pop("type"))

        id = d.pop("id")

        name = d.pop("name")

        account_id = d.pop("accountId")

        created = isoparse(d.pop("created"))

        members = []
        _members = d.pop("members", UNSET)
        for members_item_data in _members or []:
            members_item = TEContactGroupMember.from_dict(members_item_data)

            members.append(members_item)

        def _parse_assigned_customers(data: object) -> Union[None, Unset, list["TECustomer"]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                assigned_customers_type_0 = []
                _assigned_customers_type_0 = data
                for assigned_customers_type_0_item_data in _assigned_customers_type_0:
                    assigned_customers_type_0_item = TECustomer.from_dict(assigned_customers_type_0_item_data)

                    assigned_customers_type_0.append(assigned_customers_type_0_item)

                return assigned_customers_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list["TECustomer"]], data)

        assigned_customers = _parse_assigned_customers(d.pop("assignedCustomers", UNSET))

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

        te_contact_group = cls(
            type_=type_,
            id=id,
            name=name,
            account_id=account_id,
            created=created,
            members=members,
            assigned_customers=assigned_customers,
            updated=updated,
            deleted=deleted,
        )

        te_contact_group.additional_properties = d
        return te_contact_group

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
