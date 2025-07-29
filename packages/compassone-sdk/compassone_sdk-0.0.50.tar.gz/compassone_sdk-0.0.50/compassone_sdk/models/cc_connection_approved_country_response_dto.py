import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

if TYPE_CHECKING:
    from ..models.cc_iso_country_dto import CCIsoCountryDto


T = TypeVar("T", bound="CCConnectionApprovedCountryResponseDto")


@_attrs_define
class CCConnectionApprovedCountryResponseDto:
    """
    Attributes:
        id (str):
        iso_country (CCIsoCountryDto):
        created (datetime.datetime):
    """

    id: str
    iso_country: "CCIsoCountryDto"
    created: datetime.datetime
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        iso_country = self.iso_country.to_dict()

        created = self.created.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "isoCountry": iso_country,
                "created": created,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.cc_iso_country_dto import CCIsoCountryDto

        d = dict(src_dict)
        id = d.pop("id")

        iso_country = CCIsoCountryDto.from_dict(d.pop("isoCountry"))

        created = isoparse(d.pop("created"))

        cc_connection_approved_country_response_dto = cls(
            id=id,
            iso_country=iso_country,
            created=created,
        )

        cc_connection_approved_country_response_dto.additional_properties = d
        return cc_connection_approved_country_response_dto

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
