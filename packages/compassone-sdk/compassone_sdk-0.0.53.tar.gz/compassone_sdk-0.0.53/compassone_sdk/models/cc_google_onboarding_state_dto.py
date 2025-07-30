from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.cc_google_onboarding_state_dto_state import (
    CCGoogleOnboardingStateDtoState,
    check_cc_google_onboarding_state_dto_state,
)
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.cc_google_domain_wide_delegation import CCGoogleDomainWideDelegation
    from ..models.cc_google_onboarding_configuration import CCGoogleOnboardingConfiguration


T = TypeVar("T", bound="CCGoogleOnboardingStateDto")


@_attrs_define
class CCGoogleOnboardingStateDto:
    """
    Attributes:
        config (CCGoogleOnboardingConfiguration):
        id (str):
        created (str):
        state (CCGoogleOnboardingStateDtoState): State of the onboarding
        consent_url (Union[Unset, str]): URL that the user must follow to consent to permissions. This is only returned
            when the state of the onboarding is pendingConsent
        domain_wide_delegation (Union[Unset, CCGoogleDomainWideDelegation]):
        connection_id (Union[Unset, str]):
        error (Union[Unset, str]):
    """

    config: "CCGoogleOnboardingConfiguration"
    id: str
    created: str
    state: CCGoogleOnboardingStateDtoState
    consent_url: Union[Unset, str] = UNSET
    domain_wide_delegation: Union[Unset, "CCGoogleDomainWideDelegation"] = UNSET
    connection_id: Union[Unset, str] = UNSET
    error: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        config = self.config.to_dict()

        id = self.id

        created = self.created

        state: str = self.state

        consent_url = self.consent_url

        domain_wide_delegation: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.domain_wide_delegation, Unset):
            domain_wide_delegation = self.domain_wide_delegation.to_dict()

        connection_id = self.connection_id

        error = self.error

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "config": config,
                "id": id,
                "created": created,
                "state": state,
            }
        )
        if consent_url is not UNSET:
            field_dict["consentUrl"] = consent_url
        if domain_wide_delegation is not UNSET:
            field_dict["domainWideDelegation"] = domain_wide_delegation
        if connection_id is not UNSET:
            field_dict["connectionId"] = connection_id
        if error is not UNSET:
            field_dict["error"] = error

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.cc_google_domain_wide_delegation import CCGoogleDomainWideDelegation
        from ..models.cc_google_onboarding_configuration import CCGoogleOnboardingConfiguration

        d = dict(src_dict)
        config = CCGoogleOnboardingConfiguration.from_dict(d.pop("config"))

        id = d.pop("id")

        created = d.pop("created")

        state = check_cc_google_onboarding_state_dto_state(d.pop("state"))

        consent_url = d.pop("consentUrl", UNSET)

        _domain_wide_delegation = d.pop("domainWideDelegation", UNSET)
        domain_wide_delegation: Union[Unset, CCGoogleDomainWideDelegation]
        if isinstance(_domain_wide_delegation, Unset):
            domain_wide_delegation = UNSET
        else:
            domain_wide_delegation = CCGoogleDomainWideDelegation.from_dict(_domain_wide_delegation)

        connection_id = d.pop("connectionId", UNSET)

        error = d.pop("error", UNSET)

        cc_google_onboarding_state_dto = cls(
            config=config,
            id=id,
            created=created,
            state=state,
            consent_url=consent_url,
            domain_wide_delegation=domain_wide_delegation,
            connection_id=connection_id,
            error=error,
        )

        cc_google_onboarding_state_dto.additional_properties = d
        return cc_google_onboarding_state_dto

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
