import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.cc_ms_365_defense_user_iso_country import CCMs365DefenseUserIsoCountry


T = TypeVar("T", bound="CCMs365DefenseUser")


@_attrs_define
class CCMs365DefenseUser:
    """
    Attributes:
        id (str):
        email (str):
        customer_id (str):
        enabled (bool):
        licensed (bool):
        name (str):
        ms_365_defense_package_id (str):
        created (datetime.datetime):
        updated (Union[None, Unset, datetime.datetime]):
        deleted (Union[None, Unset, datetime.datetime]):
        billable (Union[Unset, bool]):
        authorized_countries (Union[Unset, list['CCMs365DefenseUserIsoCountry']]):
    """

    id: str
    email: str
    customer_id: str
    enabled: bool
    licensed: bool
    name: str
    ms_365_defense_package_id: str
    created: datetime.datetime
    updated: Union[None, Unset, datetime.datetime] = UNSET
    deleted: Union[None, Unset, datetime.datetime] = UNSET
    billable: Union[Unset, bool] = UNSET
    authorized_countries: Union[Unset, list["CCMs365DefenseUserIsoCountry"]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        email = self.email

        customer_id = self.customer_id

        enabled = self.enabled

        licensed = self.licensed

        name = self.name

        ms_365_defense_package_id = self.ms_365_defense_package_id

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

        billable = self.billable

        authorized_countries: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.authorized_countries, Unset):
            authorized_countries = []
            for authorized_countries_item_data in self.authorized_countries:
                authorized_countries_item = authorized_countries_item_data.to_dict()
                authorized_countries.append(authorized_countries_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "email": email,
                "customerId": customer_id,
                "enabled": enabled,
                "licensed": licensed,
                "name": name,
                "ms365DefensePackageId": ms_365_defense_package_id,
                "created": created,
            }
        )
        if updated is not UNSET:
            field_dict["updated"] = updated
        if deleted is not UNSET:
            field_dict["deleted"] = deleted
        if billable is not UNSET:
            field_dict["billable"] = billable
        if authorized_countries is not UNSET:
            field_dict["authorizedCountries"] = authorized_countries

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.cc_ms_365_defense_user_iso_country import CCMs365DefenseUserIsoCountry

        d = dict(src_dict)
        id = d.pop("id")

        email = d.pop("email")

        customer_id = d.pop("customerId")

        enabled = d.pop("enabled")

        licensed = d.pop("licensed")

        name = d.pop("name")

        ms_365_defense_package_id = d.pop("ms365DefensePackageId")

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

        billable = d.pop("billable", UNSET)

        authorized_countries = []
        _authorized_countries = d.pop("authorizedCountries", UNSET)
        for authorized_countries_item_data in _authorized_countries or []:
            authorized_countries_item = CCMs365DefenseUserIsoCountry.from_dict(authorized_countries_item_data)

            authorized_countries.append(authorized_countries_item)

        cc_ms_365_defense_user = cls(
            id=id,
            email=email,
            customer_id=customer_id,
            enabled=enabled,
            licensed=licensed,
            name=name,
            ms_365_defense_package_id=ms_365_defense_package_id,
            created=created,
            updated=updated,
            deleted=deleted,
            billable=billable,
            authorized_countries=authorized_countries,
        )

        cc_ms_365_defense_user.additional_properties = d
        return cc_ms_365_defense_user

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
