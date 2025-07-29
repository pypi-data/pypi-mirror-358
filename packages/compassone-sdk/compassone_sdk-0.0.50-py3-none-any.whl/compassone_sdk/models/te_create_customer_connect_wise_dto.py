from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="TECreateCustomerConnectWiseDto")


@_attrs_define
class TECreateCustomerConnectWiseDto:
    """
    Attributes:
        config_id (str):
        connectwise_customer_id (float):
        connectwise_agreement_id (float):
        enable_sync (bool):
    """

    config_id: str
    connectwise_customer_id: float
    connectwise_agreement_id: float
    enable_sync: bool
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        config_id = self.config_id

        connectwise_customer_id = self.connectwise_customer_id

        connectwise_agreement_id = self.connectwise_agreement_id

        enable_sync = self.enable_sync

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "configId": config_id,
                "connectwiseCustomerId": connectwise_customer_id,
                "connectwiseAgreementId": connectwise_agreement_id,
                "enableSync": enable_sync,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        config_id = d.pop("configId")

        connectwise_customer_id = d.pop("connectwiseCustomerId")

        connectwise_agreement_id = d.pop("connectwiseAgreementId")

        enable_sync = d.pop("enableSync")

        te_create_customer_connect_wise_dto = cls(
            config_id=config_id,
            connectwise_customer_id=connectwise_customer_id,
            connectwise_agreement_id=connectwise_agreement_id,
            enable_sync=enable_sync,
        )

        te_create_customer_connect_wise_dto.additional_properties = d
        return te_create_customer_connect_wise_dto

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
