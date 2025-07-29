import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.te_snap_customer_type import TESnapCustomerType, check_te_snap_customer_type
from ..types import UNSET, Unset

T = TypeVar("T", bound="TEV1TenantResponseDto")


@_attrs_define
class TEV1TenantResponseDto:
    """
    Attributes:
        id (str):
        name (str):
        created (datetime.datetime):
        description (Union[Unset, str]): Description of the customer
        type_ (Union[Unset, TESnapCustomerType]):
        snap_agent_url (Union[None, Unset, str]):
        contact_group_id (Union[Unset, str]):
        crm_id (Union[None, Unset, str]):
        domain (Union[None, Unset, str]):
    """

    id: str
    name: str
    created: datetime.datetime
    description: Union[Unset, str] = UNSET
    type_: Union[Unset, TESnapCustomerType] = UNSET
    snap_agent_url: Union[None, Unset, str] = UNSET
    contact_group_id: Union[Unset, str] = UNSET
    crm_id: Union[None, Unset, str] = UNSET
    domain: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        name = self.name

        created = self.created.isoformat()

        description = self.description

        type_: Union[Unset, str] = UNSET
        if not isinstance(self.type_, Unset):
            type_ = self.type_

        snap_agent_url: Union[None, Unset, str]
        if isinstance(self.snap_agent_url, Unset):
            snap_agent_url = UNSET
        else:
            snap_agent_url = self.snap_agent_url

        contact_group_id = self.contact_group_id

        crm_id: Union[None, Unset, str]
        if isinstance(self.crm_id, Unset):
            crm_id = UNSET
        else:
            crm_id = self.crm_id

        domain: Union[None, Unset, str]
        if isinstance(self.domain, Unset):
            domain = UNSET
        else:
            domain = self.domain

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "created": created,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if type_ is not UNSET:
            field_dict["type"] = type_
        if snap_agent_url is not UNSET:
            field_dict["snapAgentUrl"] = snap_agent_url
        if contact_group_id is not UNSET:
            field_dict["contactGroupId"] = contact_group_id
        if crm_id is not UNSET:
            field_dict["crmId"] = crm_id
        if domain is not UNSET:
            field_dict["domain"] = domain

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        name = d.pop("name")

        created = isoparse(d.pop("created"))

        description = d.pop("description", UNSET)

        _type_ = d.pop("type", UNSET)
        type_: Union[Unset, TESnapCustomerType]
        if isinstance(_type_, Unset):
            type_ = UNSET
        else:
            type_ = check_te_snap_customer_type(_type_)

        def _parse_snap_agent_url(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        snap_agent_url = _parse_snap_agent_url(d.pop("snapAgentUrl", UNSET))

        contact_group_id = d.pop("contactGroupId", UNSET)

        def _parse_crm_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        crm_id = _parse_crm_id(d.pop("crmId", UNSET))

        def _parse_domain(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        domain = _parse_domain(d.pop("domain", UNSET))

        tev1_tenant_response_dto = cls(
            id=id,
            name=name,
            created=created,
            description=description,
            type_=type_,
            snap_agent_url=snap_agent_url,
            contact_group_id=contact_group_id,
            crm_id=crm_id,
            domain=domain,
        )

        tev1_tenant_response_dto.additional_properties = d
        return tev1_tenant_response_dto

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
