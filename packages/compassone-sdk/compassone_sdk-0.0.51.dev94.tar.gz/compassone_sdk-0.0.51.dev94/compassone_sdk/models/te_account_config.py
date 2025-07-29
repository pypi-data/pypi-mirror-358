import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="TEAccountConfig")


@_attrs_define
class TEAccountConfig:
    """
    Attributes:
        account_id (str):
        allow_trials (bool):
        bp_response_and_compliance_enabled (bool):
        bypass_service_min_commit (bool):
        max_msp_protect_customers_allowed (float):
        cloud_response_standalone_addon_enabled (bool):
        essentials_enabled (bool):
        mdr_promotion_enabled (bool):
        created (datetime.datetime):
        mdr_essentials_enabled (Union[Unset, bool]):
        cloud_essentials_enabled (Union[Unset, bool]):
        updated (Union[None, Unset, datetime.datetime]):
        deleted (Union[None, Unset, datetime.datetime]):
    """

    account_id: str
    allow_trials: bool
    bp_response_and_compliance_enabled: bool
    bypass_service_min_commit: bool
    max_msp_protect_customers_allowed: float
    cloud_response_standalone_addon_enabled: bool
    essentials_enabled: bool
    mdr_promotion_enabled: bool
    created: datetime.datetime
    mdr_essentials_enabled: Union[Unset, bool] = UNSET
    cloud_essentials_enabled: Union[Unset, bool] = UNSET
    updated: Union[None, Unset, datetime.datetime] = UNSET
    deleted: Union[None, Unset, datetime.datetime] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        account_id = self.account_id

        allow_trials = self.allow_trials

        bp_response_and_compliance_enabled = self.bp_response_and_compliance_enabled

        bypass_service_min_commit = self.bypass_service_min_commit

        max_msp_protect_customers_allowed = self.max_msp_protect_customers_allowed

        cloud_response_standalone_addon_enabled = self.cloud_response_standalone_addon_enabled

        essentials_enabled = self.essentials_enabled

        mdr_promotion_enabled = self.mdr_promotion_enabled

        created = self.created.isoformat()

        mdr_essentials_enabled = self.mdr_essentials_enabled

        cloud_essentials_enabled = self.cloud_essentials_enabled

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
                "accountId": account_id,
                "allowTrials": allow_trials,
                "bpResponseAndComplianceEnabled": bp_response_and_compliance_enabled,
                "bypassServiceMinCommit": bypass_service_min_commit,
                "maxMspProtectCustomersAllowed": max_msp_protect_customers_allowed,
                "cloudResponseStandaloneAddonEnabled": cloud_response_standalone_addon_enabled,
                "essentialsEnabled": essentials_enabled,
                "mdrPromotionEnabled": mdr_promotion_enabled,
                "created": created,
            }
        )
        if mdr_essentials_enabled is not UNSET:
            field_dict["mdrEssentialsEnabled"] = mdr_essentials_enabled
        if cloud_essentials_enabled is not UNSET:
            field_dict["cloudEssentialsEnabled"] = cloud_essentials_enabled
        if updated is not UNSET:
            field_dict["updated"] = updated
        if deleted is not UNSET:
            field_dict["deleted"] = deleted

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        account_id = d.pop("accountId")

        allow_trials = d.pop("allowTrials")

        bp_response_and_compliance_enabled = d.pop("bpResponseAndComplianceEnabled")

        bypass_service_min_commit = d.pop("bypassServiceMinCommit")

        max_msp_protect_customers_allowed = d.pop("maxMspProtectCustomersAllowed")

        cloud_response_standalone_addon_enabled = d.pop("cloudResponseStandaloneAddonEnabled")

        essentials_enabled = d.pop("essentialsEnabled")

        mdr_promotion_enabled = d.pop("mdrPromotionEnabled")

        created = isoparse(d.pop("created"))

        mdr_essentials_enabled = d.pop("mdrEssentialsEnabled", UNSET)

        cloud_essentials_enabled = d.pop("cloudEssentialsEnabled", UNSET)

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

        te_account_config = cls(
            account_id=account_id,
            allow_trials=allow_trials,
            bp_response_and_compliance_enabled=bp_response_and_compliance_enabled,
            bypass_service_min_commit=bypass_service_min_commit,
            max_msp_protect_customers_allowed=max_msp_protect_customers_allowed,
            cloud_response_standalone_addon_enabled=cloud_response_standalone_addon_enabled,
            essentials_enabled=essentials_enabled,
            mdr_promotion_enabled=mdr_promotion_enabled,
            created=created,
            mdr_essentials_enabled=mdr_essentials_enabled,
            cloud_essentials_enabled=cloud_essentials_enabled,
            updated=updated,
            deleted=deleted,
        )

        te_account_config.additional_properties = d
        return te_account_config

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
