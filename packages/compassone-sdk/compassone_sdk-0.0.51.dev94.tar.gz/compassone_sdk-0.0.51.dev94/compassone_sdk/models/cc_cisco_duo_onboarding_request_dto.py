from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="CCCiscoDuoOnboardingRequestDto")


@_attrs_define
class CCCiscoDuoOnboardingRequestDto:
    """
    Attributes:
        host (Union[Unset, str]):
        ikey (Union[Unset, str]):
        skey (Union[Unset, str]):
    """

    host: Union[Unset, str] = UNSET
    ikey: Union[Unset, str] = UNSET
    skey: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        host = self.host

        ikey = self.ikey

        skey = self.skey

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if host is not UNSET:
            field_dict["host"] = host
        if ikey is not UNSET:
            field_dict["ikey"] = ikey
        if skey is not UNSET:
            field_dict["skey"] = skey

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        host = d.pop("host", UNSET)

        ikey = d.pop("ikey", UNSET)

        skey = d.pop("skey", UNSET)

        cc_cisco_duo_onboarding_request_dto = cls(
            host=host,
            ikey=ikey,
            skey=skey,
        )

        cc_cisco_duo_onboarding_request_dto.additional_properties = d
        return cc_cisco_duo_onboarding_request_dto

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
