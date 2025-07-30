from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.cc_connection_user_approved_country_dto import CCConnectionUserApprovedCountryDto


T = TypeVar("T", bound="CCConnectionUserDto")


@_attrs_define
class CCConnectionUserDto:
    """
    Attributes:
        id (str):
        active_approved_countries (list['CCConnectionUserApprovedCountryDto']):
        upcoming_approved_countries (list['CCConnectionUserApprovedCountryDto']):
        name (Union[Unset, str]):
        email (Union[Unset, str]):
    """

    id: str
    active_approved_countries: list["CCConnectionUserApprovedCountryDto"]
    upcoming_approved_countries: list["CCConnectionUserApprovedCountryDto"]
    name: Union[Unset, str] = UNSET
    email: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        active_approved_countries = []
        for active_approved_countries_item_data in self.active_approved_countries:
            active_approved_countries_item = active_approved_countries_item_data.to_dict()
            active_approved_countries.append(active_approved_countries_item)

        upcoming_approved_countries = []
        for upcoming_approved_countries_item_data in self.upcoming_approved_countries:
            upcoming_approved_countries_item = upcoming_approved_countries_item_data.to_dict()
            upcoming_approved_countries.append(upcoming_approved_countries_item)

        name = self.name

        email = self.email

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "activeApprovedCountries": active_approved_countries,
                "upcomingApprovedCountries": upcoming_approved_countries,
            }
        )
        if name is not UNSET:
            field_dict["name"] = name
        if email is not UNSET:
            field_dict["email"] = email

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.cc_connection_user_approved_country_dto import CCConnectionUserApprovedCountryDto

        d = dict(src_dict)
        id = d.pop("id")

        active_approved_countries = []
        _active_approved_countries = d.pop("activeApprovedCountries")
        for active_approved_countries_item_data in _active_approved_countries:
            active_approved_countries_item = CCConnectionUserApprovedCountryDto.from_dict(
                active_approved_countries_item_data
            )

            active_approved_countries.append(active_approved_countries_item)

        upcoming_approved_countries = []
        _upcoming_approved_countries = d.pop("upcomingApprovedCountries")
        for upcoming_approved_countries_item_data in _upcoming_approved_countries:
            upcoming_approved_countries_item = CCConnectionUserApprovedCountryDto.from_dict(
                upcoming_approved_countries_item_data
            )

            upcoming_approved_countries.append(upcoming_approved_countries_item)

        name = d.pop("name", UNSET)

        email = d.pop("email", UNSET)

        cc_connection_user_dto = cls(
            id=id,
            active_approved_countries=active_approved_countries,
            upcoming_approved_countries=upcoming_approved_countries,
            name=name,
            email=email,
        )

        cc_connection_user_dto.additional_properties = d
        return cc_connection_user_dto

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
