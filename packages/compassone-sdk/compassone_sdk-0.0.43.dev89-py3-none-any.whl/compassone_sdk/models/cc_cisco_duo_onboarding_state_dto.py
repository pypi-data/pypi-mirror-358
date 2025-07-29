from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.cc_cisco_duo_onboarding_state_dto_state import (
    CCCiscoDuoOnboardingStateDtoState,
    check_cc_cisco_duo_onboarding_state_dto_state,
)
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.cc_cisco_duo_onboarding_configuration import CCCiscoDuoOnboardingConfiguration


T = TypeVar("T", bound="CCCiscoDuoOnboardingStateDto")


@_attrs_define
class CCCiscoDuoOnboardingStateDto:
    """
    Attributes:
        id (str):
        created (str):
        state (CCCiscoDuoOnboardingStateDtoState): State of the onboarding
        config (CCCiscoDuoOnboardingConfiguration):
        connection_id (Union[Unset, str]):
        onboarding_id (Union[Unset, str]):
        error (Union[Unset, str]):
    """

    id: str
    created: str
    state: CCCiscoDuoOnboardingStateDtoState
    config: "CCCiscoDuoOnboardingConfiguration"
    connection_id: Union[Unset, str] = UNSET
    onboarding_id: Union[Unset, str] = UNSET
    error: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        created = self.created

        state: str = self.state

        config = self.config.to_dict()

        connection_id = self.connection_id

        onboarding_id = self.onboarding_id

        error = self.error

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "created": created,
                "state": state,
                "config": config,
            }
        )
        if connection_id is not UNSET:
            field_dict["connectionId"] = connection_id
        if onboarding_id is not UNSET:
            field_dict["onboardingId"] = onboarding_id
        if error is not UNSET:
            field_dict["error"] = error

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.cc_cisco_duo_onboarding_configuration import CCCiscoDuoOnboardingConfiguration

        d = dict(src_dict)
        id = d.pop("id")

        created = d.pop("created")

        state = check_cc_cisco_duo_onboarding_state_dto_state(d.pop("state"))

        config = CCCiscoDuoOnboardingConfiguration.from_dict(d.pop("config"))

        connection_id = d.pop("connectionId", UNSET)

        onboarding_id = d.pop("onboardingId", UNSET)

        error = d.pop("error", UNSET)

        cc_cisco_duo_onboarding_state_dto = cls(
            id=id,
            created=created,
            state=state,
            config=config,
            connection_id=connection_id,
            onboarding_id=onboarding_id,
            error=error,
        )

        cc_cisco_duo_onboarding_state_dto.additional_properties = d
        return cc_cisco_duo_onboarding_state_dto

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
