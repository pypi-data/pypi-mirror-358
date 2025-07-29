import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.cc_ms_365_defense_policy_config_extended_app_consent_state import (
    CCMs365DefensePolicyConfigExtendedAppConsentState,
    check_cc_ms_365_defense_policy_config_extended_app_consent_state,
)
from ..models.cc_ms_365_defense_policy_config_extended_external_email_warning_new_state import (
    CCMs365DefensePolicyConfigExtendedExternalEmailWarningNewState,
    check_cc_ms_365_defense_policy_config_extended_external_email_warning_new_state,
)
from ..models.cc_ms_365_defense_policy_config_extended_external_email_warning_state import (
    CCMs365DefensePolicyConfigExtendedExternalEmailWarningState,
    check_cc_ms_365_defense_policy_config_extended_external_email_warning_state,
)
from ..models.cc_ms_365_defense_policy_config_extended_safe_attachments_action import (
    CCMs365DefensePolicyConfigExtendedSafeAttachmentsAction,
    check_cc_ms_365_defense_policy_config_extended_safe_attachments_action,
)
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.cc_ms_365_defense_policy_config_formatted_data_policy_item import (
        CCMs365DefensePolicyConfigFormattedDataPolicyItem,
    )


T = TypeVar("T", bound="CCMs365DefensePolicyConfigExtended")


@_attrs_define
class CCMs365DefensePolicyConfigExtended:
    """
    Attributes:
        formatted_policies (list['CCMs365DefensePolicyConfigFormattedDataPolicyItem']):
        id (str):
        exchange_audit_all_enabled (bool):
        exchange_audit_disabled_user_email_list (list[str]):
        zap_enabled (bool):
        exchange_on_prem (bool):
        auto_forward_internet_enabled (bool):
        app_consent_state (CCMs365DefensePolicyConfigExtendedAppConsentState):
        safe_attachments_enabled (bool):
        safe_attachments_action (CCMs365DefensePolicyConfigExtendedSafeAttachmentsAction):
        secure_score_mfa_admin_count (float):
        secure_score_mfa_user_count (float):
        secure_score_total_admin_count (float):
        secure_score_total_user_count (float):
        external_email_warning_state (CCMs365DefensePolicyConfigExtendedExternalEmailWarningState):
        external_email_warning_new_state (CCMs365DefensePolicyConfigExtendedExternalEmailWarningNewState):
        external_email_warning_desired_state (bool):
        ms_365_defense_package_id (str):
        created (datetime.datetime):
        last_synced (Union[None, Unset, datetime.datetime]):
        updated (Union[None, Unset, datetime.datetime]):
        deleted (Union[None, Unset, datetime.datetime]):
    """

    formatted_policies: list["CCMs365DefensePolicyConfigFormattedDataPolicyItem"]
    id: str
    exchange_audit_all_enabled: bool
    exchange_audit_disabled_user_email_list: list[str]
    zap_enabled: bool
    exchange_on_prem: bool
    auto_forward_internet_enabled: bool
    app_consent_state: CCMs365DefensePolicyConfigExtendedAppConsentState
    safe_attachments_enabled: bool
    safe_attachments_action: CCMs365DefensePolicyConfigExtendedSafeAttachmentsAction
    secure_score_mfa_admin_count: float
    secure_score_mfa_user_count: float
    secure_score_total_admin_count: float
    secure_score_total_user_count: float
    external_email_warning_state: CCMs365DefensePolicyConfigExtendedExternalEmailWarningState
    external_email_warning_new_state: CCMs365DefensePolicyConfigExtendedExternalEmailWarningNewState
    external_email_warning_desired_state: bool
    ms_365_defense_package_id: str
    created: datetime.datetime
    last_synced: Union[None, Unset, datetime.datetime] = UNSET
    updated: Union[None, Unset, datetime.datetime] = UNSET
    deleted: Union[None, Unset, datetime.datetime] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        formatted_policies = []
        for formatted_policies_item_data in self.formatted_policies:
            formatted_policies_item = formatted_policies_item_data.to_dict()
            formatted_policies.append(formatted_policies_item)

        id = self.id

        exchange_audit_all_enabled = self.exchange_audit_all_enabled

        exchange_audit_disabled_user_email_list = self.exchange_audit_disabled_user_email_list

        zap_enabled = self.zap_enabled

        exchange_on_prem = self.exchange_on_prem

        auto_forward_internet_enabled = self.auto_forward_internet_enabled

        app_consent_state: str = self.app_consent_state

        safe_attachments_enabled = self.safe_attachments_enabled

        safe_attachments_action: str = self.safe_attachments_action

        secure_score_mfa_admin_count = self.secure_score_mfa_admin_count

        secure_score_mfa_user_count = self.secure_score_mfa_user_count

        secure_score_total_admin_count = self.secure_score_total_admin_count

        secure_score_total_user_count = self.secure_score_total_user_count

        external_email_warning_state: str = self.external_email_warning_state

        external_email_warning_new_state: str = self.external_email_warning_new_state

        external_email_warning_desired_state = self.external_email_warning_desired_state

        ms_365_defense_package_id = self.ms_365_defense_package_id

        created = self.created.isoformat()

        last_synced: Union[None, Unset, str]
        if isinstance(self.last_synced, Unset):
            last_synced = UNSET
        elif isinstance(self.last_synced, datetime.datetime):
            last_synced = self.last_synced.isoformat()
        else:
            last_synced = self.last_synced

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
                "formattedPolicies": formatted_policies,
                "id": id,
                "exchangeAuditAllEnabled": exchange_audit_all_enabled,
                "exchangeAuditDisabledUserEmailList": exchange_audit_disabled_user_email_list,
                "zapEnabled": zap_enabled,
                "exchangeOnPrem": exchange_on_prem,
                "autoForwardInternetEnabled": auto_forward_internet_enabled,
                "appConsentState": app_consent_state,
                "safeAttachmentsEnabled": safe_attachments_enabled,
                "safeAttachmentsAction": safe_attachments_action,
                "secureScoreMfaAdminCount": secure_score_mfa_admin_count,
                "secureScoreMfaUserCount": secure_score_mfa_user_count,
                "secureScoreTotalAdminCount": secure_score_total_admin_count,
                "secureScoreTotalUserCount": secure_score_total_user_count,
                "externalEmailWarningState": external_email_warning_state,
                "externalEmailWarningNewState": external_email_warning_new_state,
                "externalEmailWarningDesiredState": external_email_warning_desired_state,
                "ms365DefensePackageId": ms_365_defense_package_id,
                "created": created,
            }
        )
        if last_synced is not UNSET:
            field_dict["lastSynced"] = last_synced
        if updated is not UNSET:
            field_dict["updated"] = updated
        if deleted is not UNSET:
            field_dict["deleted"] = deleted

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.cc_ms_365_defense_policy_config_formatted_data_policy_item import (
            CCMs365DefensePolicyConfigFormattedDataPolicyItem,
        )

        d = dict(src_dict)
        formatted_policies = []
        _formatted_policies = d.pop("formattedPolicies")
        for formatted_policies_item_data in _formatted_policies:
            formatted_policies_item = CCMs365DefensePolicyConfigFormattedDataPolicyItem.from_dict(
                formatted_policies_item_data
            )

            formatted_policies.append(formatted_policies_item)

        id = d.pop("id")

        exchange_audit_all_enabled = d.pop("exchangeAuditAllEnabled")

        exchange_audit_disabled_user_email_list = cast(list[str], d.pop("exchangeAuditDisabledUserEmailList"))

        zap_enabled = d.pop("zapEnabled")

        exchange_on_prem = d.pop("exchangeOnPrem")

        auto_forward_internet_enabled = d.pop("autoForwardInternetEnabled")

        app_consent_state = check_cc_ms_365_defense_policy_config_extended_app_consent_state(d.pop("appConsentState"))

        safe_attachments_enabled = d.pop("safeAttachmentsEnabled")

        safe_attachments_action = check_cc_ms_365_defense_policy_config_extended_safe_attachments_action(
            d.pop("safeAttachmentsAction")
        )

        secure_score_mfa_admin_count = d.pop("secureScoreMfaAdminCount")

        secure_score_mfa_user_count = d.pop("secureScoreMfaUserCount")

        secure_score_total_admin_count = d.pop("secureScoreTotalAdminCount")

        secure_score_total_user_count = d.pop("secureScoreTotalUserCount")

        external_email_warning_state = check_cc_ms_365_defense_policy_config_extended_external_email_warning_state(
            d.pop("externalEmailWarningState")
        )

        external_email_warning_new_state = (
            check_cc_ms_365_defense_policy_config_extended_external_email_warning_new_state(
                d.pop("externalEmailWarningNewState")
            )
        )

        external_email_warning_desired_state = d.pop("externalEmailWarningDesiredState")

        ms_365_defense_package_id = d.pop("ms365DefensePackageId")

        created = isoparse(d.pop("created"))

        def _parse_last_synced(data: object) -> Union[None, Unset, datetime.datetime]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                last_synced_type_0 = isoparse(data)

                return last_synced_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, datetime.datetime], data)

        last_synced = _parse_last_synced(d.pop("lastSynced", UNSET))

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

        cc_ms_365_defense_policy_config_extended = cls(
            formatted_policies=formatted_policies,
            id=id,
            exchange_audit_all_enabled=exchange_audit_all_enabled,
            exchange_audit_disabled_user_email_list=exchange_audit_disabled_user_email_list,
            zap_enabled=zap_enabled,
            exchange_on_prem=exchange_on_prem,
            auto_forward_internet_enabled=auto_forward_internet_enabled,
            app_consent_state=app_consent_state,
            safe_attachments_enabled=safe_attachments_enabled,
            safe_attachments_action=safe_attachments_action,
            secure_score_mfa_admin_count=secure_score_mfa_admin_count,
            secure_score_mfa_user_count=secure_score_mfa_user_count,
            secure_score_total_admin_count=secure_score_total_admin_count,
            secure_score_total_user_count=secure_score_total_user_count,
            external_email_warning_state=external_email_warning_state,
            external_email_warning_new_state=external_email_warning_new_state,
            external_email_warning_desired_state=external_email_warning_desired_state,
            ms_365_defense_package_id=ms_365_defense_package_id,
            created=created,
            last_synced=last_synced,
            updated=updated,
            deleted=deleted,
        )

        cc_ms_365_defense_policy_config_extended.additional_properties = d
        return cc_ms_365_defense_policy_config_extended

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
