import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.te_vendor_eligible_products_aliases_item import (
    TEVendorEligibleProductsAliasesItem,
    check_te_vendor_eligible_products_aliases_item,
)
from ..models.te_vendor_name import TEVendorName, check_te_vendor_name
from ..models.te_vendor_type import TEVendorType, check_te_vendor_type
from ..types import UNSET, Unset

T = TypeVar("T", bound="TEVendor")


@_attrs_define
class TEVendor:
    """
    Attributes:
        name (TEVendorName):
        vendor_type (TEVendorType):
        id (str):
        active (bool):
        eula_accepted (bool):
        reseller_agreement (bool):
        externally_billed (bool):
        created (datetime.datetime):
        display_name (Union[Unset, str]): Used to display the name of a vendor
        cloud_response_standalone_addon_enabled (Union[Unset, bool]):
        bulk_billing_enabled (Union[Unset, bool]):
        eligible_products_aliases (Union[Unset, list[TEVendorEligibleProductsAliasesItem]]):
        updated (Union[None, Unset, datetime.datetime]):
        deleted (Union[None, Unset, datetime.datetime]):
    """

    name: TEVendorName
    vendor_type: TEVendorType
    id: str
    active: bool
    eula_accepted: bool
    reseller_agreement: bool
    externally_billed: bool
    created: datetime.datetime
    display_name: Union[Unset, str] = UNSET
    cloud_response_standalone_addon_enabled: Union[Unset, bool] = UNSET
    bulk_billing_enabled: Union[Unset, bool] = UNSET
    eligible_products_aliases: Union[Unset, list[TEVendorEligibleProductsAliasesItem]] = UNSET
    updated: Union[None, Unset, datetime.datetime] = UNSET
    deleted: Union[None, Unset, datetime.datetime] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name: str = self.name

        vendor_type: str = self.vendor_type

        id = self.id

        active = self.active

        eula_accepted = self.eula_accepted

        reseller_agreement = self.reseller_agreement

        externally_billed = self.externally_billed

        created = self.created.isoformat()

        display_name = self.display_name

        cloud_response_standalone_addon_enabled = self.cloud_response_standalone_addon_enabled

        bulk_billing_enabled = self.bulk_billing_enabled

        eligible_products_aliases: Union[Unset, list[str]] = UNSET
        if not isinstance(self.eligible_products_aliases, Unset):
            eligible_products_aliases = []
            for eligible_products_aliases_item_data in self.eligible_products_aliases:
                eligible_products_aliases_item: str = eligible_products_aliases_item_data
                eligible_products_aliases.append(eligible_products_aliases_item)

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

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "vendorType": vendor_type,
                "id": id,
                "active": active,
                "eulaAccepted": eula_accepted,
                "resellerAgreement": reseller_agreement,
                "externallyBilled": externally_billed,
                "created": created,
            }
        )
        if display_name is not UNSET:
            field_dict["displayName"] = display_name
        if cloud_response_standalone_addon_enabled is not UNSET:
            field_dict["cloudResponseStandaloneAddonEnabled"] = cloud_response_standalone_addon_enabled
        if bulk_billing_enabled is not UNSET:
            field_dict["bulkBillingEnabled"] = bulk_billing_enabled
        if eligible_products_aliases is not UNSET:
            field_dict["eligibleProductsAliases"] = eligible_products_aliases
        if updated is not UNSET:
            field_dict["updated"] = updated
        if deleted is not UNSET:
            field_dict["deleted"] = deleted

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = check_te_vendor_name(d.pop("name"))

        vendor_type = check_te_vendor_type(d.pop("vendorType"))

        id = d.pop("id")

        active = d.pop("active")

        eula_accepted = d.pop("eulaAccepted")

        reseller_agreement = d.pop("resellerAgreement")

        externally_billed = d.pop("externallyBilled")

        created = isoparse(d.pop("created"))

        display_name = d.pop("displayName", UNSET)

        cloud_response_standalone_addon_enabled = d.pop("cloudResponseStandaloneAddonEnabled", UNSET)

        bulk_billing_enabled = d.pop("bulkBillingEnabled", UNSET)

        eligible_products_aliases = []
        _eligible_products_aliases = d.pop("eligibleProductsAliases", UNSET)
        for eligible_products_aliases_item_data in _eligible_products_aliases or []:
            eligible_products_aliases_item = check_te_vendor_eligible_products_aliases_item(
                eligible_products_aliases_item_data
            )

            eligible_products_aliases.append(eligible_products_aliases_item)

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

        te_vendor = cls(
            name=name,
            vendor_type=vendor_type,
            id=id,
            active=active,
            eula_accepted=eula_accepted,
            reseller_agreement=reseller_agreement,
            externally_billed=externally_billed,
            created=created,
            display_name=display_name,
            cloud_response_standalone_addon_enabled=cloud_response_standalone_addon_enabled,
            bulk_billing_enabled=bulk_billing_enabled,
            eligible_products_aliases=eligible_products_aliases,
            updated=updated,
            deleted=deleted,
        )

        te_vendor.additional_properties = d
        return te_vendor

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
