from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="CCGoogleDomainWideDelegation")


@_attrs_define
class CCGoogleDomainWideDelegation:
    """
    Attributes:
        link (str):
        scopes (str):
        client_id (str):
    """

    link: str
    scopes: str
    client_id: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        link = self.link

        scopes = self.scopes

        client_id = self.client_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "link": link,
                "scopes": scopes,
                "clientId": client_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        link = d.pop("link")

        scopes = d.pop("scopes")

        client_id = d.pop("clientId")

        cc_google_domain_wide_delegation = cls(
            link=link,
            scopes=scopes,
            client_id=client_id,
        )

        cc_google_domain_wide_delegation.additional_properties = d
        return cc_google_domain_wide_delegation

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
