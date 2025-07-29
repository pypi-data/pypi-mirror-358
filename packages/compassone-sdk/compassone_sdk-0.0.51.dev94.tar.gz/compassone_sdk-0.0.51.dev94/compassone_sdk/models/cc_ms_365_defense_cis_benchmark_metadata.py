from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.cc_ms_365_defense_cis_benchmark_status_enum import (
    CCMs365DefenseCisBenchmarkStatusEnum,
    check_cc_ms_365_defense_cis_benchmark_status_enum,
)
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.cc_ms_365_defense_cis_benchmark_metadata_value import CCMs365DefenseCisBenchmarkMetadataValue


T = TypeVar("T", bound="CCMs365DefenseCisBenchmarkMetadata")


@_attrs_define
class CCMs365DefenseCisBenchmarkMetadata:
    """
    Attributes:
        label (str):
        status (CCMs365DefenseCisBenchmarkStatusEnum):
        value (Union[Unset, CCMs365DefenseCisBenchmarkMetadataValue]):
    """

    label: str
    status: CCMs365DefenseCisBenchmarkStatusEnum
    value: Union[Unset, "CCMs365DefenseCisBenchmarkMetadataValue"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        label = self.label

        status: str = self.status

        value: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.value, Unset):
            value = self.value.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "label": label,
                "status": status,
            }
        )
        if value is not UNSET:
            field_dict["value"] = value

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.cc_ms_365_defense_cis_benchmark_metadata_value import CCMs365DefenseCisBenchmarkMetadataValue

        d = dict(src_dict)
        label = d.pop("label")

        status = check_cc_ms_365_defense_cis_benchmark_status_enum(d.pop("status"))

        _value = d.pop("value", UNSET)
        value: Union[Unset, CCMs365DefenseCisBenchmarkMetadataValue]
        if isinstance(_value, Unset):
            value = UNSET
        else:
            value = CCMs365DefenseCisBenchmarkMetadataValue.from_dict(_value)

        cc_ms_365_defense_cis_benchmark_metadata = cls(
            label=label,
            status=status,
            value=value,
        )

        cc_ms_365_defense_cis_benchmark_metadata.additional_properties = d
        return cc_ms_365_defense_cis_benchmark_metadata

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
