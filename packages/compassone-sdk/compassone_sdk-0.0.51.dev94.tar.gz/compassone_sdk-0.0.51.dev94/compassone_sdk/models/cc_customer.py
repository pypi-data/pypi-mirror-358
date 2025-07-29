import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.cc_snap_customer_type import CCSnapCustomerType, check_cc_snap_customer_type
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.cc_ms_365_defense_package import CCMs365DefensePackage


T = TypeVar("T", bound="CCCustomer")


@_attrs_define
class CCCustomer:
    """
    Attributes:
        id (str):
        name (str):
        created (datetime.datetime):
        type_ (Union[Unset, CCSnapCustomerType]):
        updated (Union[None, Unset, datetime.datetime]):
        deleted (Union[None, Unset, datetime.datetime]):
        account_id (Union[Unset, str]):
        ms_365_defense_packages (Union[Unset, list['CCMs365DefensePackage']]):
    """

    id: str
    name: str
    created: datetime.datetime
    type_: Union[Unset, CCSnapCustomerType] = UNSET
    updated: Union[None, Unset, datetime.datetime] = UNSET
    deleted: Union[None, Unset, datetime.datetime] = UNSET
    account_id: Union[Unset, str] = UNSET
    ms_365_defense_packages: Union[Unset, list["CCMs365DefensePackage"]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        name = self.name

        created = self.created.isoformat()

        type_: Union[Unset, str] = UNSET
        if not isinstance(self.type_, Unset):
            type_ = self.type_

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

        account_id = self.account_id

        ms_365_defense_packages: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.ms_365_defense_packages, Unset):
            ms_365_defense_packages = []
            for ms_365_defense_packages_item_data in self.ms_365_defense_packages:
                ms_365_defense_packages_item = ms_365_defense_packages_item_data.to_dict()
                ms_365_defense_packages.append(ms_365_defense_packages_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "created": created,
            }
        )
        if type_ is not UNSET:
            field_dict["type"] = type_
        if updated is not UNSET:
            field_dict["updated"] = updated
        if deleted is not UNSET:
            field_dict["deleted"] = deleted
        if account_id is not UNSET:
            field_dict["accountId"] = account_id
        if ms_365_defense_packages is not UNSET:
            field_dict["ms365DefensePackages"] = ms_365_defense_packages

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.cc_ms_365_defense_package import CCMs365DefensePackage

        d = dict(src_dict)
        id = d.pop("id")

        name = d.pop("name")

        created = isoparse(d.pop("created"))

        _type_ = d.pop("type", UNSET)
        type_: Union[Unset, CCSnapCustomerType]
        if isinstance(_type_, Unset):
            type_ = UNSET
        else:
            type_ = check_cc_snap_customer_type(_type_)

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

        account_id = d.pop("accountId", UNSET)

        ms_365_defense_packages = []
        _ms_365_defense_packages = d.pop("ms365DefensePackages", UNSET)
        for ms_365_defense_packages_item_data in _ms_365_defense_packages or []:
            ms_365_defense_packages_item = CCMs365DefensePackage.from_dict(ms_365_defense_packages_item_data)

            ms_365_defense_packages.append(ms_365_defense_packages_item)

        cc_customer = cls(
            id=id,
            name=name,
            created=created,
            type_=type_,
            updated=updated,
            deleted=deleted,
            account_id=account_id,
            ms_365_defense_packages=ms_365_defense_packages,
        )

        cc_customer.additional_properties = d
        return cc_customer

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
