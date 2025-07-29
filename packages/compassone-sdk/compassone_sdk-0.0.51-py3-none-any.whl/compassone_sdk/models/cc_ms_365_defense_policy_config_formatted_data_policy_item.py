from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.cc_ms_365_defense_policy_config_formatted_data_policy_item_alias import (
    CCMs365DefensePolicyConfigFormattedDataPolicyItemAlias,
    check_cc_ms_365_defense_policy_config_formatted_data_policy_item_alias,
)
from ..models.cc_ms_365_defense_policy_config_formatted_data_policy_item_category import (
    CCMs365DefensePolicyConfigFormattedDataPolicyItemCategory,
    check_cc_ms_365_defense_policy_config_formatted_data_policy_item_category,
)
from ..models.cc_ms_365_defense_policy_config_formatted_data_policy_item_status import (
    CCMs365DefensePolicyConfigFormattedDataPolicyItemStatus,
    check_cc_ms_365_defense_policy_config_formatted_data_policy_item_status,
)
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.cc_ms_365_defense_policy_config_formatted_data_policy_item_actual_value import (
        CCMs365DefensePolicyConfigFormattedDataPolicyItemActualValue,
    )
    from ..models.cc_ms_365_defense_policy_config_formatted_data_policy_item_metadata import (
        CCMs365DefensePolicyConfigFormattedDataPolicyItemMetadata,
    )
    from ..models.cc_ms_365_defense_policy_config_formatted_data_policy_item_recommended_value import (
        CCMs365DefensePolicyConfigFormattedDataPolicyItemRecommendedValue,
    )


T = TypeVar("T", bound="CCMs365DefensePolicyConfigFormattedDataPolicyItem")


@_attrs_define
class CCMs365DefensePolicyConfigFormattedDataPolicyItem:
    """
    Attributes:
        id (str):
        alias (CCMs365DefensePolicyConfigFormattedDataPolicyItemAlias):
        category (CCMs365DefensePolicyConfigFormattedDataPolicyItemCategory):
        description (str):
        enforced (bool):
        loading (bool):
        name (str):
        status (CCMs365DefensePolicyConfigFormattedDataPolicyItemStatus):
        actual_value (Union[Unset, CCMs365DefensePolicyConfigFormattedDataPolicyItemActualValue]):
        link (Union[Unset, str]):
        metadata (Union[Unset, CCMs365DefensePolicyConfigFormattedDataPolicyItemMetadata]):
        recommended_value (Union[Unset, CCMs365DefensePolicyConfigFormattedDataPolicyItemRecommendedValue]):
        recommended_label (Union[Unset, str]):
    """

    id: str
    alias: CCMs365DefensePolicyConfigFormattedDataPolicyItemAlias
    category: CCMs365DefensePolicyConfigFormattedDataPolicyItemCategory
    description: str
    enforced: bool
    loading: bool
    name: str
    status: CCMs365DefensePolicyConfigFormattedDataPolicyItemStatus
    actual_value: Union[Unset, "CCMs365DefensePolicyConfigFormattedDataPolicyItemActualValue"] = UNSET
    link: Union[Unset, str] = UNSET
    metadata: Union[Unset, "CCMs365DefensePolicyConfigFormattedDataPolicyItemMetadata"] = UNSET
    recommended_value: Union[Unset, "CCMs365DefensePolicyConfigFormattedDataPolicyItemRecommendedValue"] = UNSET
    recommended_label: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        alias: str = self.alias

        category: str = self.category

        description = self.description

        enforced = self.enforced

        loading = self.loading

        name = self.name

        status: str = self.status

        actual_value: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.actual_value, Unset):
            actual_value = self.actual_value.to_dict()

        link = self.link

        metadata: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()

        recommended_value: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.recommended_value, Unset):
            recommended_value = self.recommended_value.to_dict()

        recommended_label = self.recommended_label

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "alias": alias,
                "category": category,
                "description": description,
                "enforced": enforced,
                "loading": loading,
                "name": name,
                "status": status,
            }
        )
        if actual_value is not UNSET:
            field_dict["actualValue"] = actual_value
        if link is not UNSET:
            field_dict["link"] = link
        if metadata is not UNSET:
            field_dict["metadata"] = metadata
        if recommended_value is not UNSET:
            field_dict["recommendedValue"] = recommended_value
        if recommended_label is not UNSET:
            field_dict["recommendedLabel"] = recommended_label

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.cc_ms_365_defense_policy_config_formatted_data_policy_item_actual_value import (
            CCMs365DefensePolicyConfigFormattedDataPolicyItemActualValue,
        )
        from ..models.cc_ms_365_defense_policy_config_formatted_data_policy_item_metadata import (
            CCMs365DefensePolicyConfigFormattedDataPolicyItemMetadata,
        )
        from ..models.cc_ms_365_defense_policy_config_formatted_data_policy_item_recommended_value import (
            CCMs365DefensePolicyConfigFormattedDataPolicyItemRecommendedValue,
        )

        d = dict(src_dict)
        id = d.pop("id")

        alias = check_cc_ms_365_defense_policy_config_formatted_data_policy_item_alias(d.pop("alias"))

        category = check_cc_ms_365_defense_policy_config_formatted_data_policy_item_category(d.pop("category"))

        description = d.pop("description")

        enforced = d.pop("enforced")

        loading = d.pop("loading")

        name = d.pop("name")

        status = check_cc_ms_365_defense_policy_config_formatted_data_policy_item_status(d.pop("status"))

        _actual_value = d.pop("actualValue", UNSET)
        actual_value: Union[Unset, CCMs365DefensePolicyConfigFormattedDataPolicyItemActualValue]
        if isinstance(_actual_value, Unset):
            actual_value = UNSET
        else:
            actual_value = CCMs365DefensePolicyConfigFormattedDataPolicyItemActualValue.from_dict(_actual_value)

        link = d.pop("link", UNSET)

        _metadata = d.pop("metadata", UNSET)
        metadata: Union[Unset, CCMs365DefensePolicyConfigFormattedDataPolicyItemMetadata]
        if isinstance(_metadata, Unset):
            metadata = UNSET
        else:
            metadata = CCMs365DefensePolicyConfigFormattedDataPolicyItemMetadata.from_dict(_metadata)

        _recommended_value = d.pop("recommendedValue", UNSET)
        recommended_value: Union[Unset, CCMs365DefensePolicyConfigFormattedDataPolicyItemRecommendedValue]
        if isinstance(_recommended_value, Unset):
            recommended_value = UNSET
        else:
            recommended_value = CCMs365DefensePolicyConfigFormattedDataPolicyItemRecommendedValue.from_dict(
                _recommended_value
            )

        recommended_label = d.pop("recommendedLabel", UNSET)

        cc_ms_365_defense_policy_config_formatted_data_policy_item = cls(
            id=id,
            alias=alias,
            category=category,
            description=description,
            enforced=enforced,
            loading=loading,
            name=name,
            status=status,
            actual_value=actual_value,
            link=link,
            metadata=metadata,
            recommended_value=recommended_value,
            recommended_label=recommended_label,
        )

        cc_ms_365_defense_policy_config_formatted_data_policy_item.additional_properties = d
        return cc_ms_365_defense_policy_config_formatted_data_policy_item

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
