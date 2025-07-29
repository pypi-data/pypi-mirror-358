import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="CCPostUserAuthorizedIsoCountryDto")


@_attrs_define
class CCPostUserAuthorizedIsoCountryDto:
    """
    Attributes:
        iso_country_code (str):
        start_date (Union[None, Unset, datetime.datetime]):
        end_date (Union[None, Unset, datetime.datetime]):
    """

    iso_country_code: str
    start_date: Union[None, Unset, datetime.datetime] = UNSET
    end_date: Union[None, Unset, datetime.datetime] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        iso_country_code = self.iso_country_code

        start_date: Union[None, Unset, str]
        if isinstance(self.start_date, Unset):
            start_date = UNSET
        elif isinstance(self.start_date, datetime.datetime):
            start_date = self.start_date.isoformat()
        else:
            start_date = self.start_date

        end_date: Union[None, Unset, str]
        if isinstance(self.end_date, Unset):
            end_date = UNSET
        elif isinstance(self.end_date, datetime.datetime):
            end_date = self.end_date.isoformat()
        else:
            end_date = self.end_date

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "isoCountryCode": iso_country_code,
            }
        )
        if start_date is not UNSET:
            field_dict["startDate"] = start_date
        if end_date is not UNSET:
            field_dict["endDate"] = end_date

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        iso_country_code = d.pop("isoCountryCode")

        def _parse_start_date(data: object) -> Union[None, Unset, datetime.datetime]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                start_date_type_0 = isoparse(data)

                return start_date_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, datetime.datetime], data)

        start_date = _parse_start_date(d.pop("startDate", UNSET))

        def _parse_end_date(data: object) -> Union[None, Unset, datetime.datetime]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                end_date_type_0 = isoparse(data)

                return end_date_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, datetime.datetime], data)

        end_date = _parse_end_date(d.pop("endDate", UNSET))

        cc_post_user_authorized_iso_country_dto = cls(
            iso_country_code=iso_country_code,
            start_date=start_date,
            end_date=end_date,
        )

        cc_post_user_authorized_iso_country_dto.additional_properties = d
        return cc_post_user_authorized_iso_country_dto

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
