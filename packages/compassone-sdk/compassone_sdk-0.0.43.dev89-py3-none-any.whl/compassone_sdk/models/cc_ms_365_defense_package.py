import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.cc_ms_365_defense_package_onboarding_stage import (
    CCMs365DefensePackageOnboardingStage,
    check_cc_ms_365_defense_package_onboarding_stage,
)
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.cc_iso_country import CCIsoCountry
    from ..models.cc_ms_365_defense_cis_benchmark import CCMs365DefenseCisBenchmark
    from ..models.cc_ms_365_defense_event import CCMs365DefenseEvent
    from ..models.cc_ms_365_defense_policy_config_extended import CCMs365DefensePolicyConfigExtended
    from ..models.cc_ms_365_defense_user import CCMs365DefenseUser


T = TypeVar("T", bound="CCMs365DefensePackage")


@_attrs_define
class CCMs365DefensePackage:
    """
    Attributes:
        audit_enabled (bool):
        global_admin_role_assigned (bool):
        onboarded (bool):
        can_webhook_subscribe (bool):
        consented_to_new_perms (bool):
        onboarding_stage (CCMs365DefensePackageOnboardingStage):
        s_2_set_new_banner_complete (bool):
        s_3_remove_transport_rule_complete (bool):
        s_4_sync_already_featured_complete (bool):
        customer_id (str):
        id (str):
        created (datetime.datetime):
        snap_name (Union[None, Unset, str]):
        snap_enabled (Union[None, Unset, bool]):
        snap_package_id (Union[None, Unset, str]):
        updated (Union[None, Unset, datetime.datetime]):
        deleted (Union[None, Unset, datetime.datetime]):
        tenant_id (Union[None, Unset, str]):
        primary_domain (Union[None, Unset, str]):
        principal_id (Union[None, Unset, str]):
        ms_365_defense_policy_config (Union[Unset, CCMs365DefensePolicyConfigExtended]):
        ms_redirect_url (Union[None, Unset, str]):
        cis_benchmarks_last_synced (Union[None, Unset, datetime.datetime]):
        ms_365_defense_events (Union[Unset, list['CCMs365DefenseEvent']]):
        ms_365_defense_users (Union[Unset, list['CCMs365DefenseUser']]):
        ms_365_defense_cis_benchmarks (Union[Unset, list['CCMs365DefenseCisBenchmark']]):
        authorized_countries (Union[Unset, list['CCIsoCountry']]):
    """

    audit_enabled: bool
    global_admin_role_assigned: bool
    onboarded: bool
    can_webhook_subscribe: bool
    consented_to_new_perms: bool
    onboarding_stage: CCMs365DefensePackageOnboardingStage
    s_2_set_new_banner_complete: bool
    s_3_remove_transport_rule_complete: bool
    s_4_sync_already_featured_complete: bool
    customer_id: str
    id: str
    created: datetime.datetime
    snap_name: Union[None, Unset, str] = UNSET
    snap_enabled: Union[None, Unset, bool] = UNSET
    snap_package_id: Union[None, Unset, str] = UNSET
    updated: Union[None, Unset, datetime.datetime] = UNSET
    deleted: Union[None, Unset, datetime.datetime] = UNSET
    tenant_id: Union[None, Unset, str] = UNSET
    primary_domain: Union[None, Unset, str] = UNSET
    principal_id: Union[None, Unset, str] = UNSET
    ms_365_defense_policy_config: Union[Unset, "CCMs365DefensePolicyConfigExtended"] = UNSET
    ms_redirect_url: Union[None, Unset, str] = UNSET
    cis_benchmarks_last_synced: Union[None, Unset, datetime.datetime] = UNSET
    ms_365_defense_events: Union[Unset, list["CCMs365DefenseEvent"]] = UNSET
    ms_365_defense_users: Union[Unset, list["CCMs365DefenseUser"]] = UNSET
    ms_365_defense_cis_benchmarks: Union[Unset, list["CCMs365DefenseCisBenchmark"]] = UNSET
    authorized_countries: Union[Unset, list["CCIsoCountry"]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        audit_enabled = self.audit_enabled

        global_admin_role_assigned = self.global_admin_role_assigned

        onboarded = self.onboarded

        can_webhook_subscribe = self.can_webhook_subscribe

        consented_to_new_perms = self.consented_to_new_perms

        onboarding_stage: str = self.onboarding_stage

        s_2_set_new_banner_complete = self.s_2_set_new_banner_complete

        s_3_remove_transport_rule_complete = self.s_3_remove_transport_rule_complete

        s_4_sync_already_featured_complete = self.s_4_sync_already_featured_complete

        customer_id = self.customer_id

        id = self.id

        created = self.created.isoformat()

        snap_name: Union[None, Unset, str]
        if isinstance(self.snap_name, Unset):
            snap_name = UNSET
        else:
            snap_name = self.snap_name

        snap_enabled: Union[None, Unset, bool]
        if isinstance(self.snap_enabled, Unset):
            snap_enabled = UNSET
        else:
            snap_enabled = self.snap_enabled

        snap_package_id: Union[None, Unset, str]
        if isinstance(self.snap_package_id, Unset):
            snap_package_id = UNSET
        else:
            snap_package_id = self.snap_package_id

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

        tenant_id: Union[None, Unset, str]
        if isinstance(self.tenant_id, Unset):
            tenant_id = UNSET
        else:
            tenant_id = self.tenant_id

        primary_domain: Union[None, Unset, str]
        if isinstance(self.primary_domain, Unset):
            primary_domain = UNSET
        else:
            primary_domain = self.primary_domain

        principal_id: Union[None, Unset, str]
        if isinstance(self.principal_id, Unset):
            principal_id = UNSET
        else:
            principal_id = self.principal_id

        ms_365_defense_policy_config: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.ms_365_defense_policy_config, Unset):
            ms_365_defense_policy_config = self.ms_365_defense_policy_config.to_dict()

        ms_redirect_url: Union[None, Unset, str]
        if isinstance(self.ms_redirect_url, Unset):
            ms_redirect_url = UNSET
        else:
            ms_redirect_url = self.ms_redirect_url

        cis_benchmarks_last_synced: Union[None, Unset, str]
        if isinstance(self.cis_benchmarks_last_synced, Unset):
            cis_benchmarks_last_synced = UNSET
        elif isinstance(self.cis_benchmarks_last_synced, datetime.datetime):
            cis_benchmarks_last_synced = self.cis_benchmarks_last_synced.isoformat()
        else:
            cis_benchmarks_last_synced = self.cis_benchmarks_last_synced

        ms_365_defense_events: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.ms_365_defense_events, Unset):
            ms_365_defense_events = []
            for ms_365_defense_events_item_data in self.ms_365_defense_events:
                ms_365_defense_events_item = ms_365_defense_events_item_data.to_dict()
                ms_365_defense_events.append(ms_365_defense_events_item)

        ms_365_defense_users: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.ms_365_defense_users, Unset):
            ms_365_defense_users = []
            for ms_365_defense_users_item_data in self.ms_365_defense_users:
                ms_365_defense_users_item = ms_365_defense_users_item_data.to_dict()
                ms_365_defense_users.append(ms_365_defense_users_item)

        ms_365_defense_cis_benchmarks: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.ms_365_defense_cis_benchmarks, Unset):
            ms_365_defense_cis_benchmarks = []
            for ms_365_defense_cis_benchmarks_item_data in self.ms_365_defense_cis_benchmarks:
                ms_365_defense_cis_benchmarks_item = ms_365_defense_cis_benchmarks_item_data.to_dict()
                ms_365_defense_cis_benchmarks.append(ms_365_defense_cis_benchmarks_item)

        authorized_countries: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.authorized_countries, Unset):
            authorized_countries = []
            for authorized_countries_item_data in self.authorized_countries:
                authorized_countries_item = authorized_countries_item_data.to_dict()
                authorized_countries.append(authorized_countries_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "auditEnabled": audit_enabled,
                "globalAdminRoleAssigned": global_admin_role_assigned,
                "onboarded": onboarded,
                "canWebhookSubscribe": can_webhook_subscribe,
                "consentedToNewPerms": consented_to_new_perms,
                "onboardingStage": onboarding_stage,
                "s2SetNewBannerComplete": s_2_set_new_banner_complete,
                "s3RemoveTransportRuleComplete": s_3_remove_transport_rule_complete,
                "s4SyncAlreadyFeaturedComplete": s_4_sync_already_featured_complete,
                "customerId": customer_id,
                "id": id,
                "created": created,
            }
        )
        if snap_name is not UNSET:
            field_dict["snapName"] = snap_name
        if snap_enabled is not UNSET:
            field_dict["snapEnabled"] = snap_enabled
        if snap_package_id is not UNSET:
            field_dict["snapPackageId"] = snap_package_id
        if updated is not UNSET:
            field_dict["updated"] = updated
        if deleted is not UNSET:
            field_dict["deleted"] = deleted
        if tenant_id is not UNSET:
            field_dict["tenantId"] = tenant_id
        if primary_domain is not UNSET:
            field_dict["primaryDomain"] = primary_domain
        if principal_id is not UNSET:
            field_dict["principalId"] = principal_id
        if ms_365_defense_policy_config is not UNSET:
            field_dict["ms365DefensePolicyConfig"] = ms_365_defense_policy_config
        if ms_redirect_url is not UNSET:
            field_dict["msRedirectUrl"] = ms_redirect_url
        if cis_benchmarks_last_synced is not UNSET:
            field_dict["cisBenchmarksLastSynced"] = cis_benchmarks_last_synced
        if ms_365_defense_events is not UNSET:
            field_dict["ms365DefenseEvents"] = ms_365_defense_events
        if ms_365_defense_users is not UNSET:
            field_dict["ms365DefenseUsers"] = ms_365_defense_users
        if ms_365_defense_cis_benchmarks is not UNSET:
            field_dict["ms365DefenseCisBenchmarks"] = ms_365_defense_cis_benchmarks
        if authorized_countries is not UNSET:
            field_dict["authorizedCountries"] = authorized_countries

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.cc_iso_country import CCIsoCountry
        from ..models.cc_ms_365_defense_cis_benchmark import CCMs365DefenseCisBenchmark
        from ..models.cc_ms_365_defense_event import CCMs365DefenseEvent
        from ..models.cc_ms_365_defense_policy_config_extended import CCMs365DefensePolicyConfigExtended
        from ..models.cc_ms_365_defense_user import CCMs365DefenseUser

        d = dict(src_dict)
        audit_enabled = d.pop("auditEnabled")

        global_admin_role_assigned = d.pop("globalAdminRoleAssigned")

        onboarded = d.pop("onboarded")

        can_webhook_subscribe = d.pop("canWebhookSubscribe")

        consented_to_new_perms = d.pop("consentedToNewPerms")

        onboarding_stage = check_cc_ms_365_defense_package_onboarding_stage(d.pop("onboardingStage"))

        s_2_set_new_banner_complete = d.pop("s2SetNewBannerComplete")

        s_3_remove_transport_rule_complete = d.pop("s3RemoveTransportRuleComplete")

        s_4_sync_already_featured_complete = d.pop("s4SyncAlreadyFeaturedComplete")

        customer_id = d.pop("customerId")

        id = d.pop("id")

        created = isoparse(d.pop("created"))

        def _parse_snap_name(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        snap_name = _parse_snap_name(d.pop("snapName", UNSET))

        def _parse_snap_enabled(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        snap_enabled = _parse_snap_enabled(d.pop("snapEnabled", UNSET))

        def _parse_snap_package_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        snap_package_id = _parse_snap_package_id(d.pop("snapPackageId", UNSET))

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

        def _parse_tenant_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        tenant_id = _parse_tenant_id(d.pop("tenantId", UNSET))

        def _parse_primary_domain(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        primary_domain = _parse_primary_domain(d.pop("primaryDomain", UNSET))

        def _parse_principal_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        principal_id = _parse_principal_id(d.pop("principalId", UNSET))

        _ms_365_defense_policy_config = d.pop("ms365DefensePolicyConfig", UNSET)
        ms_365_defense_policy_config: Union[Unset, CCMs365DefensePolicyConfigExtended]
        if isinstance(_ms_365_defense_policy_config, Unset):
            ms_365_defense_policy_config = UNSET
        else:
            ms_365_defense_policy_config = CCMs365DefensePolicyConfigExtended.from_dict(_ms_365_defense_policy_config)

        def _parse_ms_redirect_url(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        ms_redirect_url = _parse_ms_redirect_url(d.pop("msRedirectUrl", UNSET))

        def _parse_cis_benchmarks_last_synced(data: object) -> Union[None, Unset, datetime.datetime]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                cis_benchmarks_last_synced_type_0 = isoparse(data)

                return cis_benchmarks_last_synced_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, datetime.datetime], data)

        cis_benchmarks_last_synced = _parse_cis_benchmarks_last_synced(d.pop("cisBenchmarksLastSynced", UNSET))

        ms_365_defense_events = []
        _ms_365_defense_events = d.pop("ms365DefenseEvents", UNSET)
        for ms_365_defense_events_item_data in _ms_365_defense_events or []:
            ms_365_defense_events_item = CCMs365DefenseEvent.from_dict(ms_365_defense_events_item_data)

            ms_365_defense_events.append(ms_365_defense_events_item)

        ms_365_defense_users = []
        _ms_365_defense_users = d.pop("ms365DefenseUsers", UNSET)
        for ms_365_defense_users_item_data in _ms_365_defense_users or []:
            ms_365_defense_users_item = CCMs365DefenseUser.from_dict(ms_365_defense_users_item_data)

            ms_365_defense_users.append(ms_365_defense_users_item)

        ms_365_defense_cis_benchmarks = []
        _ms_365_defense_cis_benchmarks = d.pop("ms365DefenseCisBenchmarks", UNSET)
        for ms_365_defense_cis_benchmarks_item_data in _ms_365_defense_cis_benchmarks or []:
            ms_365_defense_cis_benchmarks_item = CCMs365DefenseCisBenchmark.from_dict(
                ms_365_defense_cis_benchmarks_item_data
            )

            ms_365_defense_cis_benchmarks.append(ms_365_defense_cis_benchmarks_item)

        authorized_countries = []
        _authorized_countries = d.pop("authorizedCountries", UNSET)
        for authorized_countries_item_data in _authorized_countries or []:
            authorized_countries_item = CCIsoCountry.from_dict(authorized_countries_item_data)

            authorized_countries.append(authorized_countries_item)

        cc_ms_365_defense_package = cls(
            audit_enabled=audit_enabled,
            global_admin_role_assigned=global_admin_role_assigned,
            onboarded=onboarded,
            can_webhook_subscribe=can_webhook_subscribe,
            consented_to_new_perms=consented_to_new_perms,
            onboarding_stage=onboarding_stage,
            s_2_set_new_banner_complete=s_2_set_new_banner_complete,
            s_3_remove_transport_rule_complete=s_3_remove_transport_rule_complete,
            s_4_sync_already_featured_complete=s_4_sync_already_featured_complete,
            customer_id=customer_id,
            id=id,
            created=created,
            snap_name=snap_name,
            snap_enabled=snap_enabled,
            snap_package_id=snap_package_id,
            updated=updated,
            deleted=deleted,
            tenant_id=tenant_id,
            primary_domain=primary_domain,
            principal_id=principal_id,
            ms_365_defense_policy_config=ms_365_defense_policy_config,
            ms_redirect_url=ms_redirect_url,
            cis_benchmarks_last_synced=cis_benchmarks_last_synced,
            ms_365_defense_events=ms_365_defense_events,
            ms_365_defense_users=ms_365_defense_users,
            ms_365_defense_cis_benchmarks=ms_365_defense_cis_benchmarks,
            authorized_countries=authorized_countries,
        )

        cc_ms_365_defense_package.additional_properties = d
        return cc_ms_365_defense_package

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
