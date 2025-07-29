import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.te_account_billing_model import TEAccountBillingModel, check_te_account_billing_model
from ..models.te_account_billing_version import TEAccountBillingVersion, check_te_account_billing_version
from ..models.te_account_partnership_type import TEAccountPartnershipType, check_te_account_partnership_type
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.te_account_config import TEAccountConfig
    from ..models.te_billing_contract import TEBillingContract
    from ..models.te_invite import TEInvite
    from ..models.te_vendor import TEVendor


T = TypeVar("T", bound="TEAccount")


@_attrs_define
class TEAccount:
    """
    Attributes:
        billing_model (TEAccountBillingModel):
        id (str):
        name (str):
        vendor_id (str):
        allow_paid_converts (bool):
        bundle_override (bool):
        created (datetime.datetime):
        billing_version (Union[Unset, TEAccountBillingVersion]):
        partnership_type (Union[Unset, TEAccountPartnershipType]):
        trial_credits (Union[None, Unset, float]): Use config.allowTrials instead
        vendor (Union[Unset, TEVendor]):
        allow_vendor_transfer (Union[Unset, bool]):
        billing_contracts (Union[Unset, list['TEBillingContract']]):
        crm_id (Union[None, Unset, str]):
        external_id (Union[None, Unset, str]):
        internal_notes (Union[None, Unset, str]):
        country (Union[None, Unset, str]):
        state (Union[None, Unset, str]):
        invites (Union[None, Unset, list['TEInvite']]):
        activation_date (Union[None, Unset, datetime.datetime]):
        config (Union[Unset, TEAccountConfig]):
        deactivation_date (Union[None, Unset, datetime.datetime]):
        updated (Union[None, Unset, datetime.datetime]):
        deleted (Union[None, Unset, datetime.datetime]):
    """

    billing_model: TEAccountBillingModel
    id: str
    name: str
    vendor_id: str
    allow_paid_converts: bool
    bundle_override: bool
    created: datetime.datetime
    billing_version: Union[Unset, TEAccountBillingVersion] = UNSET
    partnership_type: Union[Unset, TEAccountPartnershipType] = UNSET
    trial_credits: Union[None, Unset, float] = UNSET
    vendor: Union[Unset, "TEVendor"] = UNSET
    allow_vendor_transfer: Union[Unset, bool] = UNSET
    billing_contracts: Union[Unset, list["TEBillingContract"]] = UNSET
    crm_id: Union[None, Unset, str] = UNSET
    external_id: Union[None, Unset, str] = UNSET
    internal_notes: Union[None, Unset, str] = UNSET
    country: Union[None, Unset, str] = UNSET
    state: Union[None, Unset, str] = UNSET
    invites: Union[None, Unset, list["TEInvite"]] = UNSET
    activation_date: Union[None, Unset, datetime.datetime] = UNSET
    config: Union[Unset, "TEAccountConfig"] = UNSET
    deactivation_date: Union[None, Unset, datetime.datetime] = UNSET
    updated: Union[None, Unset, datetime.datetime] = UNSET
    deleted: Union[None, Unset, datetime.datetime] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        billing_model: str = self.billing_model

        id = self.id

        name = self.name

        vendor_id = self.vendor_id

        allow_paid_converts = self.allow_paid_converts

        bundle_override = self.bundle_override

        created = self.created.isoformat()

        billing_version: Union[Unset, str] = UNSET
        if not isinstance(self.billing_version, Unset):
            billing_version = self.billing_version

        partnership_type: Union[Unset, str] = UNSET
        if not isinstance(self.partnership_type, Unset):
            partnership_type = self.partnership_type

        trial_credits: Union[None, Unset, float]
        if isinstance(self.trial_credits, Unset):
            trial_credits = UNSET
        else:
            trial_credits = self.trial_credits

        vendor: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.vendor, Unset):
            vendor = self.vendor.to_dict()

        allow_vendor_transfer = self.allow_vendor_transfer

        billing_contracts: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.billing_contracts, Unset):
            billing_contracts = []
            for billing_contracts_item_data in self.billing_contracts:
                billing_contracts_item = billing_contracts_item_data.to_dict()
                billing_contracts.append(billing_contracts_item)

        crm_id: Union[None, Unset, str]
        if isinstance(self.crm_id, Unset):
            crm_id = UNSET
        else:
            crm_id = self.crm_id

        external_id: Union[None, Unset, str]
        if isinstance(self.external_id, Unset):
            external_id = UNSET
        else:
            external_id = self.external_id

        internal_notes: Union[None, Unset, str]
        if isinstance(self.internal_notes, Unset):
            internal_notes = UNSET
        else:
            internal_notes = self.internal_notes

        country: Union[None, Unset, str]
        if isinstance(self.country, Unset):
            country = UNSET
        else:
            country = self.country

        state: Union[None, Unset, str]
        if isinstance(self.state, Unset):
            state = UNSET
        else:
            state = self.state

        invites: Union[None, Unset, list[dict[str, Any]]]
        if isinstance(self.invites, Unset):
            invites = UNSET
        elif isinstance(self.invites, list):
            invites = []
            for invites_type_0_item_data in self.invites:
                invites_type_0_item = invites_type_0_item_data.to_dict()
                invites.append(invites_type_0_item)

        else:
            invites = self.invites

        activation_date: Union[None, Unset, str]
        if isinstance(self.activation_date, Unset):
            activation_date = UNSET
        elif isinstance(self.activation_date, datetime.datetime):
            activation_date = self.activation_date.isoformat()
        else:
            activation_date = self.activation_date

        config: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.config, Unset):
            config = self.config.to_dict()

        deactivation_date: Union[None, Unset, str]
        if isinstance(self.deactivation_date, Unset):
            deactivation_date = UNSET
        elif isinstance(self.deactivation_date, datetime.datetime):
            deactivation_date = self.deactivation_date.isoformat()
        else:
            deactivation_date = self.deactivation_date

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
                "billingModel": billing_model,
                "id": id,
                "name": name,
                "vendorId": vendor_id,
                "allowPaidConverts": allow_paid_converts,
                "bundleOverride": bundle_override,
                "created": created,
            }
        )
        if billing_version is not UNSET:
            field_dict["billingVersion"] = billing_version
        if partnership_type is not UNSET:
            field_dict["partnershipType"] = partnership_type
        if trial_credits is not UNSET:
            field_dict["trialCredits"] = trial_credits
        if vendor is not UNSET:
            field_dict["vendor"] = vendor
        if allow_vendor_transfer is not UNSET:
            field_dict["allowVendorTransfer"] = allow_vendor_transfer
        if billing_contracts is not UNSET:
            field_dict["billingContracts"] = billing_contracts
        if crm_id is not UNSET:
            field_dict["crmId"] = crm_id
        if external_id is not UNSET:
            field_dict["externalId"] = external_id
        if internal_notes is not UNSET:
            field_dict["internalNotes"] = internal_notes
        if country is not UNSET:
            field_dict["country"] = country
        if state is not UNSET:
            field_dict["state"] = state
        if invites is not UNSET:
            field_dict["invites"] = invites
        if activation_date is not UNSET:
            field_dict["activationDate"] = activation_date
        if config is not UNSET:
            field_dict["config"] = config
        if deactivation_date is not UNSET:
            field_dict["deactivationDate"] = deactivation_date
        if updated is not UNSET:
            field_dict["updated"] = updated
        if deleted is not UNSET:
            field_dict["deleted"] = deleted

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.te_account_config import TEAccountConfig
        from ..models.te_billing_contract import TEBillingContract
        from ..models.te_invite import TEInvite
        from ..models.te_vendor import TEVendor

        d = dict(src_dict)
        billing_model = check_te_account_billing_model(d.pop("billingModel"))

        id = d.pop("id")

        name = d.pop("name")

        vendor_id = d.pop("vendorId")

        allow_paid_converts = d.pop("allowPaidConverts")

        bundle_override = d.pop("bundleOverride")

        created = isoparse(d.pop("created"))

        _billing_version = d.pop("billingVersion", UNSET)
        billing_version: Union[Unset, TEAccountBillingVersion]
        if isinstance(_billing_version, Unset):
            billing_version = UNSET
        else:
            billing_version = check_te_account_billing_version(_billing_version)

        _partnership_type = d.pop("partnershipType", UNSET)
        partnership_type: Union[Unset, TEAccountPartnershipType]
        if isinstance(_partnership_type, Unset):
            partnership_type = UNSET
        else:
            partnership_type = check_te_account_partnership_type(_partnership_type)

        def _parse_trial_credits(data: object) -> Union[None, Unset, float]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, float], data)

        trial_credits = _parse_trial_credits(d.pop("trialCredits", UNSET))

        _vendor = d.pop("vendor", UNSET)
        vendor: Union[Unset, TEVendor]
        if isinstance(_vendor, Unset):
            vendor = UNSET
        else:
            vendor = TEVendor.from_dict(_vendor)

        allow_vendor_transfer = d.pop("allowVendorTransfer", UNSET)

        billing_contracts = []
        _billing_contracts = d.pop("billingContracts", UNSET)
        for billing_contracts_item_data in _billing_contracts or []:
            billing_contracts_item = TEBillingContract.from_dict(billing_contracts_item_data)

            billing_contracts.append(billing_contracts_item)

        def _parse_crm_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        crm_id = _parse_crm_id(d.pop("crmId", UNSET))

        def _parse_external_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        external_id = _parse_external_id(d.pop("externalId", UNSET))

        def _parse_internal_notes(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        internal_notes = _parse_internal_notes(d.pop("internalNotes", UNSET))

        def _parse_country(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        country = _parse_country(d.pop("country", UNSET))

        def _parse_state(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        state = _parse_state(d.pop("state", UNSET))

        def _parse_invites(data: object) -> Union[None, Unset, list["TEInvite"]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                invites_type_0 = []
                _invites_type_0 = data
                for invites_type_0_item_data in _invites_type_0:
                    invites_type_0_item = TEInvite.from_dict(invites_type_0_item_data)

                    invites_type_0.append(invites_type_0_item)

                return invites_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list["TEInvite"]], data)

        invites = _parse_invites(d.pop("invites", UNSET))

        def _parse_activation_date(data: object) -> Union[None, Unset, datetime.datetime]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                activation_date_type_0 = isoparse(data)

                return activation_date_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, datetime.datetime], data)

        activation_date = _parse_activation_date(d.pop("activationDate", UNSET))

        _config = d.pop("config", UNSET)
        config: Union[Unset, TEAccountConfig]
        if isinstance(_config, Unset):
            config = UNSET
        else:
            config = TEAccountConfig.from_dict(_config)

        def _parse_deactivation_date(data: object) -> Union[None, Unset, datetime.datetime]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                deactivation_date_type_0 = isoparse(data)

                return deactivation_date_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, datetime.datetime], data)

        deactivation_date = _parse_deactivation_date(d.pop("deactivationDate", UNSET))

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

        te_account = cls(
            billing_model=billing_model,
            id=id,
            name=name,
            vendor_id=vendor_id,
            allow_paid_converts=allow_paid_converts,
            bundle_override=bundle_override,
            created=created,
            billing_version=billing_version,
            partnership_type=partnership_type,
            trial_credits=trial_credits,
            vendor=vendor,
            allow_vendor_transfer=allow_vendor_transfer,
            billing_contracts=billing_contracts,
            crm_id=crm_id,
            external_id=external_id,
            internal_notes=internal_notes,
            country=country,
            state=state,
            invites=invites,
            activation_date=activation_date,
            config=config,
            deactivation_date=deactivation_date,
            updated=updated,
            deleted=deleted,
        )

        te_account.additional_properties = d
        return te_account

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
