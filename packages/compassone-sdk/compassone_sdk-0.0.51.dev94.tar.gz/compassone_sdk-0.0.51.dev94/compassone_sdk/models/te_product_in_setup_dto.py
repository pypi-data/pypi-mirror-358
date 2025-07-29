from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.te_product_alias import TEProductAlias, check_te_product_alias
from ..models.te_product_family import TEProductFamily, check_te_product_family
from ..models.te_product_type import TEProductType, check_te_product_type
from ..types import UNSET, Unset

T = TypeVar("T", bound="TEProductInSetupDto")


@_attrs_define
class TEProductInSetupDto:
    """
    Attributes:
        alias (TEProductAlias):
        type_ (TEProductType):
        family (TEProductFamily):
        is_bundle (bool):
        bundled_items (list['TEProductInSetupDto']):
        id (str):
        name (str):
        description (Union[None, Unset, str]):
        months_to_renew (Union[None, Unset, float]):
        more_link (Union[None, Unset, str]):
    """

    alias: TEProductAlias
    type_: TEProductType
    family: TEProductFamily
    is_bundle: bool
    bundled_items: list["TEProductInSetupDto"]
    id: str
    name: str
    description: Union[None, Unset, str] = UNSET
    months_to_renew: Union[None, Unset, float] = UNSET
    more_link: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        alias: str = self.alias

        type_: str = self.type_

        family: str = self.family

        is_bundle = self.is_bundle

        bundled_items = []
        for bundled_items_item_data in self.bundled_items:
            bundled_items_item = bundled_items_item_data.to_dict()
            bundled_items.append(bundled_items_item)

        id = self.id

        name = self.name

        description: Union[None, Unset, str]
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        months_to_renew: Union[None, Unset, float]
        if isinstance(self.months_to_renew, Unset):
            months_to_renew = UNSET
        else:
            months_to_renew = self.months_to_renew

        more_link: Union[None, Unset, str]
        if isinstance(self.more_link, Unset):
            more_link = UNSET
        else:
            more_link = self.more_link

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "alias": alias,
                "type": type_,
                "family": family,
                "isBundle": is_bundle,
                "bundledItems": bundled_items,
                "id": id,
                "name": name,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if months_to_renew is not UNSET:
            field_dict["monthsToRenew"] = months_to_renew
        if more_link is not UNSET:
            field_dict["moreLink"] = more_link

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        alias = check_te_product_alias(d.pop("alias"))

        type_ = check_te_product_type(d.pop("type"))

        family = check_te_product_family(d.pop("family"))

        is_bundle = d.pop("isBundle")

        bundled_items = []
        _bundled_items = d.pop("bundledItems")
        for bundled_items_item_data in _bundled_items:
            bundled_items_item = TEProductInSetupDto.from_dict(bundled_items_item_data)

            bundled_items.append(bundled_items_item)

        id = d.pop("id")

        name = d.pop("name")

        def _parse_description(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        description = _parse_description(d.pop("description", UNSET))

        def _parse_months_to_renew(data: object) -> Union[None, Unset, float]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, float], data)

        months_to_renew = _parse_months_to_renew(d.pop("monthsToRenew", UNSET))

        def _parse_more_link(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        more_link = _parse_more_link(d.pop("moreLink", UNSET))

        te_product_in_setup_dto = cls(
            alias=alias,
            type_=type_,
            family=family,
            is_bundle=is_bundle,
            bundled_items=bundled_items,
            id=id,
            name=name,
            description=description,
            months_to_renew=months_to_renew,
            more_link=more_link,
        )

        te_product_in_setup_dto.additional_properties = d
        return te_product_in_setup_dto

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
