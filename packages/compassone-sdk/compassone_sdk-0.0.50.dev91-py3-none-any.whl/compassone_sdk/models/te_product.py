import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.te_product_alias import TEProductAlias, check_te_product_alias
from ..models.te_product_elegibility import TEProductElegibility, check_te_product_elegibility
from ..models.te_product_family import TEProductFamily, check_te_product_family
from ..models.te_product_type import TEProductType, check_te_product_type
from ..models.te_snap_package_type import TESnapPackageType, check_te_snap_package_type
from ..types import UNSET, Unset

T = TypeVar("T", bound="TEProduct")


@_attrs_define
class TEProduct:
    """
    Attributes:
        alias (TEProductAlias):
        type_ (TEProductType):
        family (TEProductFamily):
        enables_snap_package_types (list[TESnapPackageType]):
        elegibility (TEProductElegibility):
        id (str):
        name (str):
        can_be_standalone (bool):
        only_for_bundles (bool):
        created (datetime.datetime):
        is_eol (bool):
        bundled_items (Union[None, Unset, list['TEProduct']]):
        add_ons (Union[None, Unset, list['TEProduct']]):
        is_bundle (Union[Unset, bool]):
        description (Union[None, Unset, str]):
        more_link (Union[None, Unset, str]):
        updated (Union[None, Unset, datetime.datetime]):
        deleted (Union[None, Unset, datetime.datetime]):
        months_to_renew (Union[None, Unset, float]):
        auto_renew_warning (Union[None, Unset, bool]):
    """

    alias: TEProductAlias
    type_: TEProductType
    family: TEProductFamily
    enables_snap_package_types: list[TESnapPackageType]
    elegibility: TEProductElegibility
    id: str
    name: str
    can_be_standalone: bool
    only_for_bundles: bool
    created: datetime.datetime
    is_eol: bool
    bundled_items: Union[None, Unset, list["TEProduct"]] = UNSET
    add_ons: Union[None, Unset, list["TEProduct"]] = UNSET
    is_bundle: Union[Unset, bool] = UNSET
    description: Union[None, Unset, str] = UNSET
    more_link: Union[None, Unset, str] = UNSET
    updated: Union[None, Unset, datetime.datetime] = UNSET
    deleted: Union[None, Unset, datetime.datetime] = UNSET
    months_to_renew: Union[None, Unset, float] = UNSET
    auto_renew_warning: Union[None, Unset, bool] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        alias: str = self.alias

        type_: str = self.type_

        family: str = self.family

        enables_snap_package_types = []
        for enables_snap_package_types_item_data in self.enables_snap_package_types:
            enables_snap_package_types_item: str = enables_snap_package_types_item_data
            enables_snap_package_types.append(enables_snap_package_types_item)

        elegibility: str = self.elegibility

        id = self.id

        name = self.name

        can_be_standalone = self.can_be_standalone

        only_for_bundles = self.only_for_bundles

        created = self.created.isoformat()

        is_eol = self.is_eol

        bundled_items: Union[None, Unset, list[dict[str, Any]]]
        if isinstance(self.bundled_items, Unset):
            bundled_items = UNSET
        elif isinstance(self.bundled_items, list):
            bundled_items = []
            for bundled_items_type_0_item_data in self.bundled_items:
                bundled_items_type_0_item = bundled_items_type_0_item_data.to_dict()
                bundled_items.append(bundled_items_type_0_item)

        else:
            bundled_items = self.bundled_items

        add_ons: Union[None, Unset, list[dict[str, Any]]]
        if isinstance(self.add_ons, Unset):
            add_ons = UNSET
        elif isinstance(self.add_ons, list):
            add_ons = []
            for add_ons_type_0_item_data in self.add_ons:
                add_ons_type_0_item = add_ons_type_0_item_data.to_dict()
                add_ons.append(add_ons_type_0_item)

        else:
            add_ons = self.add_ons

        is_bundle = self.is_bundle

        description: Union[None, Unset, str]
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        more_link: Union[None, Unset, str]
        if isinstance(self.more_link, Unset):
            more_link = UNSET
        else:
            more_link = self.more_link

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

        months_to_renew: Union[None, Unset, float]
        if isinstance(self.months_to_renew, Unset):
            months_to_renew = UNSET
        else:
            months_to_renew = self.months_to_renew

        auto_renew_warning: Union[None, Unset, bool]
        if isinstance(self.auto_renew_warning, Unset):
            auto_renew_warning = UNSET
        else:
            auto_renew_warning = self.auto_renew_warning

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "alias": alias,
                "type": type_,
                "family": family,
                "enablesSnapPackageTypes": enables_snap_package_types,
                "elegibility": elegibility,
                "id": id,
                "name": name,
                "canBeStandalone": can_be_standalone,
                "onlyForBundles": only_for_bundles,
                "created": created,
                "isEol": is_eol,
            }
        )
        if bundled_items is not UNSET:
            field_dict["bundledItems"] = bundled_items
        if add_ons is not UNSET:
            field_dict["addOns"] = add_ons
        if is_bundle is not UNSET:
            field_dict["isBundle"] = is_bundle
        if description is not UNSET:
            field_dict["description"] = description
        if more_link is not UNSET:
            field_dict["moreLink"] = more_link
        if updated is not UNSET:
            field_dict["updated"] = updated
        if deleted is not UNSET:
            field_dict["deleted"] = deleted
        if months_to_renew is not UNSET:
            field_dict["monthsToRenew"] = months_to_renew
        if auto_renew_warning is not UNSET:
            field_dict["autoRenewWarning"] = auto_renew_warning

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        alias = check_te_product_alias(d.pop("alias"))

        type_ = check_te_product_type(d.pop("type"))

        family = check_te_product_family(d.pop("family"))

        enables_snap_package_types = []
        _enables_snap_package_types = d.pop("enablesSnapPackageTypes")
        for enables_snap_package_types_item_data in _enables_snap_package_types:
            enables_snap_package_types_item = check_te_snap_package_type(enables_snap_package_types_item_data)

            enables_snap_package_types.append(enables_snap_package_types_item)

        elegibility = check_te_product_elegibility(d.pop("elegibility"))

        id = d.pop("id")

        name = d.pop("name")

        can_be_standalone = d.pop("canBeStandalone")

        only_for_bundles = d.pop("onlyForBundles")

        created = isoparse(d.pop("created"))

        is_eol = d.pop("isEol")

        def _parse_bundled_items(data: object) -> Union[None, Unset, list["TEProduct"]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                bundled_items_type_0 = []
                _bundled_items_type_0 = data
                for bundled_items_type_0_item_data in _bundled_items_type_0:
                    bundled_items_type_0_item = TEProduct.from_dict(bundled_items_type_0_item_data)

                    bundled_items_type_0.append(bundled_items_type_0_item)

                return bundled_items_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list["TEProduct"]], data)

        bundled_items = _parse_bundled_items(d.pop("bundledItems", UNSET))

        def _parse_add_ons(data: object) -> Union[None, Unset, list["TEProduct"]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                add_ons_type_0 = []
                _add_ons_type_0 = data
                for add_ons_type_0_item_data in _add_ons_type_0:
                    add_ons_type_0_item = TEProduct.from_dict(add_ons_type_0_item_data)

                    add_ons_type_0.append(add_ons_type_0_item)

                return add_ons_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list["TEProduct"]], data)

        add_ons = _parse_add_ons(d.pop("addOns", UNSET))

        is_bundle = d.pop("isBundle", UNSET)

        def _parse_description(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        description = _parse_description(d.pop("description", UNSET))

        def _parse_more_link(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        more_link = _parse_more_link(d.pop("moreLink", UNSET))

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

        def _parse_months_to_renew(data: object) -> Union[None, Unset, float]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, float], data)

        months_to_renew = _parse_months_to_renew(d.pop("monthsToRenew", UNSET))

        def _parse_auto_renew_warning(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        auto_renew_warning = _parse_auto_renew_warning(d.pop("autoRenewWarning", UNSET))

        te_product = cls(
            alias=alias,
            type_=type_,
            family=family,
            enables_snap_package_types=enables_snap_package_types,
            elegibility=elegibility,
            id=id,
            name=name,
            can_be_standalone=can_be_standalone,
            only_for_bundles=only_for_bundles,
            created=created,
            is_eol=is_eol,
            bundled_items=bundled_items,
            add_ons=add_ons,
            is_bundle=is_bundle,
            description=description,
            more_link=more_link,
            updated=updated,
            deleted=deleted,
            months_to_renew=months_to_renew,
            auto_renew_warning=auto_renew_warning,
        )

        te_product.additional_properties = d
        return te_product

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
