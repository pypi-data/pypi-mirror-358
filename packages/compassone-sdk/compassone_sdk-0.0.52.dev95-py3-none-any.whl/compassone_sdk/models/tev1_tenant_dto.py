import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.te_tenant_status import TETenantStatus, check_te_tenant_status
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.tev1_contact_group_with_members_dto import TEV1ContactGroupWithMembersDto


T = TypeVar("T", bound="TEV1TenantDto")


@_attrs_define
class TEV1TenantDto:
    """
    Attributes:
        status (TETenantStatus):
        informational_alerts_emails (list[str]):
        mdr_reports_emails (list[str]):
        dark_web_alerts_emails (list[str]):
        id (str):
        name (str):
        created (datetime.datetime):
        enable_delivery_email (bool):
        contact_group (Union[Unset, TEV1ContactGroupWithMembersDto]):
        account_id (Union[None, Unset, str]):
        description (Union[None, Unset, str]):
        domain (Union[None, Unset, str]):
        snap_agent_url (Union[None, Unset, str]):
        industry_type (Union[Unset, str]):
    """

    status: TETenantStatus
    informational_alerts_emails: list[str]
    mdr_reports_emails: list[str]
    dark_web_alerts_emails: list[str]
    id: str
    name: str
    created: datetime.datetime
    enable_delivery_email: bool
    contact_group: Union[Unset, "TEV1ContactGroupWithMembersDto"] = UNSET
    account_id: Union[None, Unset, str] = UNSET
    description: Union[None, Unset, str] = UNSET
    domain: Union[None, Unset, str] = UNSET
    snap_agent_url: Union[None, Unset, str] = UNSET
    industry_type: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        status: str = self.status

        informational_alerts_emails = self.informational_alerts_emails

        mdr_reports_emails = self.mdr_reports_emails

        dark_web_alerts_emails = self.dark_web_alerts_emails

        id = self.id

        name = self.name

        created = self.created.isoformat()

        enable_delivery_email = self.enable_delivery_email

        contact_group: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.contact_group, Unset):
            contact_group = self.contact_group.to_dict()

        account_id: Union[None, Unset, str]
        if isinstance(self.account_id, Unset):
            account_id = UNSET
        else:
            account_id = self.account_id

        description: Union[None, Unset, str]
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        domain: Union[None, Unset, str]
        if isinstance(self.domain, Unset):
            domain = UNSET
        else:
            domain = self.domain

        snap_agent_url: Union[None, Unset, str]
        if isinstance(self.snap_agent_url, Unset):
            snap_agent_url = UNSET
        else:
            snap_agent_url = self.snap_agent_url

        industry_type = self.industry_type

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "status": status,
                "informationalAlertsEmails": informational_alerts_emails,
                "mdrReportsEmails": mdr_reports_emails,
                "darkWebAlertsEmails": dark_web_alerts_emails,
                "id": id,
                "name": name,
                "created": created,
                "enableDeliveryEmail": enable_delivery_email,
            }
        )
        if contact_group is not UNSET:
            field_dict["contactGroup"] = contact_group
        if account_id is not UNSET:
            field_dict["accountId"] = account_id
        if description is not UNSET:
            field_dict["description"] = description
        if domain is not UNSET:
            field_dict["domain"] = domain
        if snap_agent_url is not UNSET:
            field_dict["snapAgentUrl"] = snap_agent_url
        if industry_type is not UNSET:
            field_dict["industryType"] = industry_type

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.tev1_contact_group_with_members_dto import TEV1ContactGroupWithMembersDto

        d = dict(src_dict)
        status = check_te_tenant_status(d.pop("status"))

        informational_alerts_emails = cast(list[str], d.pop("informationalAlertsEmails"))

        mdr_reports_emails = cast(list[str], d.pop("mdrReportsEmails"))

        dark_web_alerts_emails = cast(list[str], d.pop("darkWebAlertsEmails"))

        id = d.pop("id")

        name = d.pop("name")

        created = isoparse(d.pop("created"))

        enable_delivery_email = d.pop("enableDeliveryEmail")

        _contact_group = d.pop("contactGroup", UNSET)
        contact_group: Union[Unset, TEV1ContactGroupWithMembersDto]
        if isinstance(_contact_group, Unset):
            contact_group = UNSET
        else:
            contact_group = TEV1ContactGroupWithMembersDto.from_dict(_contact_group)

        def _parse_account_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        account_id = _parse_account_id(d.pop("accountId", UNSET))

        def _parse_description(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        description = _parse_description(d.pop("description", UNSET))

        def _parse_domain(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        domain = _parse_domain(d.pop("domain", UNSET))

        def _parse_snap_agent_url(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        snap_agent_url = _parse_snap_agent_url(d.pop("snapAgentUrl", UNSET))

        industry_type = d.pop("industryType", UNSET)

        tev1_tenant_dto = cls(
            status=status,
            informational_alerts_emails=informational_alerts_emails,
            mdr_reports_emails=mdr_reports_emails,
            dark_web_alerts_emails=dark_web_alerts_emails,
            id=id,
            name=name,
            created=created,
            enable_delivery_email=enable_delivery_email,
            contact_group=contact_group,
            account_id=account_id,
            description=description,
            domain=domain,
            snap_agent_url=snap_agent_url,
            industry_type=industry_type,
        )

        tev1_tenant_dto.additional_properties = d
        return tev1_tenant_dto

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
