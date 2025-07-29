from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.cc_connection_user_approved_country_dto import CCConnectionUserApprovedCountryDto


T = TypeVar("T", bound="CCPaginatedConnectionUsersApprovedCountriesResponseDto")


@_attrs_define
class CCPaginatedConnectionUsersApprovedCountriesResponseDto:
    """
    Attributes:
        items (list['CCConnectionUserApprovedCountryDto']): Items returned from the database
        start (float): Index of the first item returned from the database
        end (float): Index of the last item returned from the database
        total (float): Total number of items returned from the database
        take (Union[Unset, float]): Max number of items to return from the database Default: 100.0.
        skip (Union[Unset, float]): Number of database items to skip Default: 0.0.
    """

    items: list["CCConnectionUserApprovedCountryDto"]
    start: float
    end: float
    total: float
    take: Union[Unset, float] = 100.0
    skip: Union[Unset, float] = 0.0
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        items = []
        for items_item_data in self.items:
            items_item = items_item_data.to_dict()
            items.append(items_item)

        start = self.start

        end = self.end

        total = self.total

        take = self.take

        skip = self.skip

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "items": items,
                "start": start,
                "end": end,
                "total": total,
            }
        )
        if take is not UNSET:
            field_dict["take"] = take
        if skip is not UNSET:
            field_dict["skip"] = skip

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.cc_connection_user_approved_country_dto import CCConnectionUserApprovedCountryDto

        d = dict(src_dict)
        items = []
        _items = d.pop("items")
        for items_item_data in _items:
            items_item = CCConnectionUserApprovedCountryDto.from_dict(items_item_data)

            items.append(items_item)

        start = d.pop("start")

        end = d.pop("end")

        total = d.pop("total")

        take = d.pop("take", UNSET)

        skip = d.pop("skip", UNSET)

        cc_paginated_connection_users_approved_countries_response_dto = cls(
            items=items,
            start=start,
            end=end,
            total=total,
            take=take,
            skip=skip,
        )

        cc_paginated_connection_users_approved_countries_response_dto.additional_properties = d
        return cc_paginated_connection_users_approved_countries_response_dto

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
