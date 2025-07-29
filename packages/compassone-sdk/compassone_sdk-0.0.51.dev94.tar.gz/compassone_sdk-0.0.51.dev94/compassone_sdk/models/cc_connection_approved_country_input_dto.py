from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="CCConnectionApprovedCountryInputDto")


@_attrs_define
class CCConnectionApprovedCountryInputDto:
    """
    Attributes:
        iso_country_code (str): The ISO 3166-1 alpha-2 country code to approve. Example: US.
    """

    iso_country_code: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        iso_country_code = self.iso_country_code

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "isoCountryCode": iso_country_code,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        iso_country_code = d.pop("isoCountryCode")

        cc_connection_approved_country_input_dto = cls(
            iso_country_code=iso_country_code,
        )

        cc_connection_approved_country_input_dto.additional_properties = d
        return cc_connection_approved_country_input_dto

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
