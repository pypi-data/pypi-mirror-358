import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.cc_iso_country_dto import CCIsoCountryDto


T = TypeVar("T", bound="CCConnectionUserApprovedCountryDto")


@_attrs_define
class CCConnectionUserApprovedCountryDto:
    """
    Attributes:
        id (str):
        connection_user_id (str):
        iso_country (CCIsoCountryDto):
        created (datetime.datetime):
        end_date (Union[Unset, datetime.datetime]):
        start_date (Union[Unset, datetime.datetime]):
    """

    id: str
    connection_user_id: str
    iso_country: "CCIsoCountryDto"
    created: datetime.datetime
    end_date: Union[Unset, datetime.datetime] = UNSET
    start_date: Union[Unset, datetime.datetime] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        connection_user_id = self.connection_user_id

        iso_country = self.iso_country.to_dict()

        created = self.created.isoformat()

        end_date: Union[Unset, str] = UNSET
        if not isinstance(self.end_date, Unset):
            end_date = self.end_date.isoformat()

        start_date: Union[Unset, str] = UNSET
        if not isinstance(self.start_date, Unset):
            start_date = self.start_date.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "connectionUserId": connection_user_id,
                "isoCountry": iso_country,
                "created": created,
            }
        )
        if end_date is not UNSET:
            field_dict["endDate"] = end_date
        if start_date is not UNSET:
            field_dict["startDate"] = start_date

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.cc_iso_country_dto import CCIsoCountryDto

        d = dict(src_dict)
        id = d.pop("id")

        connection_user_id = d.pop("connectionUserId")

        iso_country = CCIsoCountryDto.from_dict(d.pop("isoCountry"))

        created = isoparse(d.pop("created"))

        _end_date = d.pop("endDate", UNSET)
        end_date: Union[Unset, datetime.datetime]
        if isinstance(_end_date, Unset):
            end_date = UNSET
        else:
            end_date = isoparse(_end_date)

        _start_date = d.pop("startDate", UNSET)
        start_date: Union[Unset, datetime.datetime]
        if isinstance(_start_date, Unset):
            start_date = UNSET
        else:
            start_date = isoparse(_start_date)

        cc_connection_user_approved_country_dto = cls(
            id=id,
            connection_user_id=connection_user_id,
            iso_country=iso_country,
            created=created,
            end_date=end_date,
            start_date=start_date,
        )

        cc_connection_user_approved_country_dto.additional_properties = d
        return cc_connection_user_approved_country_dto

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
