import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.te_account_billing_version import TEAccountBillingVersion, check_te_account_billing_version
from ..models.te_account_partnership_type import TEAccountPartnershipType, check_te_account_partnership_type
from ..types import UNSET, Unset

T = TypeVar("T", bound="TEV1AccountDto")


@_attrs_define
class TEV1AccountDto:
    """
    Attributes:
        id (str):
        name (str):
        vendor_id (str):
        created (datetime.datetime):
        partnership_type (Union[Unset, TEAccountPartnershipType]):
        billing_version (Union[Unset, TEAccountBillingVersion]):
    """

    id: str
    name: str
    vendor_id: str
    created: datetime.datetime
    partnership_type: Union[Unset, TEAccountPartnershipType] = UNSET
    billing_version: Union[Unset, TEAccountBillingVersion] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        name = self.name

        vendor_id = self.vendor_id

        created = self.created.isoformat()

        partnership_type: Union[Unset, str] = UNSET
        if not isinstance(self.partnership_type, Unset):
            partnership_type = self.partnership_type

        billing_version: Union[Unset, str] = UNSET
        if not isinstance(self.billing_version, Unset):
            billing_version = self.billing_version

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "vendorId": vendor_id,
                "created": created,
            }
        )
        if partnership_type is not UNSET:
            field_dict["partnershipType"] = partnership_type
        if billing_version is not UNSET:
            field_dict["billingVersion"] = billing_version

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        name = d.pop("name")

        vendor_id = d.pop("vendorId")

        created = isoparse(d.pop("created"))

        _partnership_type = d.pop("partnershipType", UNSET)
        partnership_type: Union[Unset, TEAccountPartnershipType]
        if isinstance(_partnership_type, Unset):
            partnership_type = UNSET
        else:
            partnership_type = check_te_account_partnership_type(_partnership_type)

        _billing_version = d.pop("billingVersion", UNSET)
        billing_version: Union[Unset, TEAccountBillingVersion]
        if isinstance(_billing_version, Unset):
            billing_version = UNSET
        else:
            billing_version = check_te_account_billing_version(_billing_version)

        tev1_account_dto = cls(
            id=id,
            name=name,
            vendor_id=vendor_id,
            created=created,
            partnership_type=partnership_type,
            billing_version=billing_version,
        )

        tev1_account_dto.additional_properties = d
        return tev1_account_dto

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
