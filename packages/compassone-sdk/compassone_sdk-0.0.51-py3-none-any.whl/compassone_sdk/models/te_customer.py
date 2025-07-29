import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.te_customer_relation_type import TECustomerRelationType, check_te_customer_relation_type
from ..models.te_customer_source_type import TECustomerSourceType, check_te_customer_source_type
from ..models.te_snap_customer_type import TESnapCustomerType, check_te_snap_customer_type
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.te_account import TEAccount
    from ..models.te_contact_group import TEContactGroup
    from ..models.te_create_customer_connect_wise_dto import TECreateCustomerConnectWiseDto
    from ..models.te_customer_config import TECustomerConfig
    from ..models.te_customer_mapped_meta_type_0 import TECustomerMappedMetaType0
    from ..models.te_customer_product import TECustomerProduct
    from ..models.te_unified_customer_config import TEUnifiedCustomerConfig


T = TypeVar("T", bound="TECustomer")


@_attrs_define
class TECustomer:
    """
    Attributes:
        type_ (TESnapCustomerType):
        relation_type (TECustomerRelationType):
        id (str):
        name (str):
        enable_delivery_email (bool):
        bill_overage (bool):
        created (datetime.datetime):
        customer_products (Union[Unset, list['TECustomerProduct']]):
        connect_wise_company_id (Union[None, Unset, float]):
        connect_wise_note_id (Union[None, Unset, float]):
        connect_wise_contact_id (Union[None, Unset, float]):
        contact_group (Union[Unset, TEContactGroup]):
        source (Union[Unset, TECustomerSourceType]):
        description (Union[None, Unset, str]):
        account_id (Union[None, Unset, str]):
        account (Union['TEAccount', None, Unset]):
        snap_agent_url (Union[None, Unset, str]):
        industry_type (Union[Unset, str]):
        mapped_meta (Union['TECustomerMappedMetaType0', None, Unset]):
        customer_config (Union[Unset, TECustomerConfig]):
        unified_customer_config (Union[Unset, TEUnifiedCustomerConfig]):
        contact_group_id (Union[None, Unset, str]):
        auto_renew (Union[None, Unset, bool]):
        domain (Union[None, Unset, str]):
        crm_id (Union[None, Unset, str]):
        internal (Union[Unset, bool]):
        deactivation_date (Union[None, Unset, datetime.datetime]):
        updated (Union[None, Unset, datetime.datetime]):
        deleted (Union[None, Unset, datetime.datetime]):
        connect_wise_mapping (Union[Unset, TECreateCustomerConnectWiseDto]):
    """

    type_: TESnapCustomerType
    relation_type: TECustomerRelationType
    id: str
    name: str
    enable_delivery_email: bool
    bill_overage: bool
    created: datetime.datetime
    customer_products: Union[Unset, list["TECustomerProduct"]] = UNSET
    connect_wise_company_id: Union[None, Unset, float] = UNSET
    connect_wise_note_id: Union[None, Unset, float] = UNSET
    connect_wise_contact_id: Union[None, Unset, float] = UNSET
    contact_group: Union[Unset, "TEContactGroup"] = UNSET
    source: Union[Unset, TECustomerSourceType] = UNSET
    description: Union[None, Unset, str] = UNSET
    account_id: Union[None, Unset, str] = UNSET
    account: Union["TEAccount", None, Unset] = UNSET
    snap_agent_url: Union[None, Unset, str] = UNSET
    industry_type: Union[Unset, str] = UNSET
    mapped_meta: Union["TECustomerMappedMetaType0", None, Unset] = UNSET
    customer_config: Union[Unset, "TECustomerConfig"] = UNSET
    unified_customer_config: Union[Unset, "TEUnifiedCustomerConfig"] = UNSET
    contact_group_id: Union[None, Unset, str] = UNSET
    auto_renew: Union[None, Unset, bool] = UNSET
    domain: Union[None, Unset, str] = UNSET
    crm_id: Union[None, Unset, str] = UNSET
    internal: Union[Unset, bool] = UNSET
    deactivation_date: Union[None, Unset, datetime.datetime] = UNSET
    updated: Union[None, Unset, datetime.datetime] = UNSET
    deleted: Union[None, Unset, datetime.datetime] = UNSET
    connect_wise_mapping: Union[Unset, "TECreateCustomerConnectWiseDto"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.te_account import TEAccount
        from ..models.te_customer_mapped_meta_type_0 import TECustomerMappedMetaType0

        type_: str = self.type_

        relation_type: str = self.relation_type

        id = self.id

        name = self.name

        enable_delivery_email = self.enable_delivery_email

        bill_overage = self.bill_overage

        created = self.created.isoformat()

        customer_products: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.customer_products, Unset):
            customer_products = []
            for customer_products_item_data in self.customer_products:
                customer_products_item = customer_products_item_data.to_dict()
                customer_products.append(customer_products_item)

        connect_wise_company_id: Union[None, Unset, float]
        if isinstance(self.connect_wise_company_id, Unset):
            connect_wise_company_id = UNSET
        else:
            connect_wise_company_id = self.connect_wise_company_id

        connect_wise_note_id: Union[None, Unset, float]
        if isinstance(self.connect_wise_note_id, Unset):
            connect_wise_note_id = UNSET
        else:
            connect_wise_note_id = self.connect_wise_note_id

        connect_wise_contact_id: Union[None, Unset, float]
        if isinstance(self.connect_wise_contact_id, Unset):
            connect_wise_contact_id = UNSET
        else:
            connect_wise_contact_id = self.connect_wise_contact_id

        contact_group: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.contact_group, Unset):
            contact_group = self.contact_group.to_dict()

        source: Union[Unset, str] = UNSET
        if not isinstance(self.source, Unset):
            source = self.source

        description: Union[None, Unset, str]
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        account_id: Union[None, Unset, str]
        if isinstance(self.account_id, Unset):
            account_id = UNSET
        else:
            account_id = self.account_id

        account: Union[None, Unset, dict[str, Any]]
        if isinstance(self.account, Unset):
            account = UNSET
        elif isinstance(self.account, TEAccount):
            account = self.account.to_dict()
        else:
            account = self.account

        snap_agent_url: Union[None, Unset, str]
        if isinstance(self.snap_agent_url, Unset):
            snap_agent_url = UNSET
        else:
            snap_agent_url = self.snap_agent_url

        industry_type = self.industry_type

        mapped_meta: Union[None, Unset, dict[str, Any]]
        if isinstance(self.mapped_meta, Unset):
            mapped_meta = UNSET
        elif isinstance(self.mapped_meta, TECustomerMappedMetaType0):
            mapped_meta = self.mapped_meta.to_dict()
        else:
            mapped_meta = self.mapped_meta

        customer_config: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.customer_config, Unset):
            customer_config = self.customer_config.to_dict()

        unified_customer_config: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.unified_customer_config, Unset):
            unified_customer_config = self.unified_customer_config.to_dict()

        contact_group_id: Union[None, Unset, str]
        if isinstance(self.contact_group_id, Unset):
            contact_group_id = UNSET
        else:
            contact_group_id = self.contact_group_id

        auto_renew: Union[None, Unset, bool]
        if isinstance(self.auto_renew, Unset):
            auto_renew = UNSET
        else:
            auto_renew = self.auto_renew

        domain: Union[None, Unset, str]
        if isinstance(self.domain, Unset):
            domain = UNSET
        else:
            domain = self.domain

        crm_id: Union[None, Unset, str]
        if isinstance(self.crm_id, Unset):
            crm_id = UNSET
        else:
            crm_id = self.crm_id

        internal = self.internal

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

        connect_wise_mapping: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.connect_wise_mapping, Unset):
            connect_wise_mapping = self.connect_wise_mapping.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "type": type_,
                "relationType": relation_type,
                "id": id,
                "name": name,
                "enableDeliveryEmail": enable_delivery_email,
                "billOverage": bill_overage,
                "created": created,
            }
        )
        if customer_products is not UNSET:
            field_dict["customerProducts"] = customer_products
        if connect_wise_company_id is not UNSET:
            field_dict["connectWiseCompanyId"] = connect_wise_company_id
        if connect_wise_note_id is not UNSET:
            field_dict["connectWiseNoteId"] = connect_wise_note_id
        if connect_wise_contact_id is not UNSET:
            field_dict["connectWiseContactId"] = connect_wise_contact_id
        if contact_group is not UNSET:
            field_dict["contactGroup"] = contact_group
        if source is not UNSET:
            field_dict["source"] = source
        if description is not UNSET:
            field_dict["description"] = description
        if account_id is not UNSET:
            field_dict["accountId"] = account_id
        if account is not UNSET:
            field_dict["account"] = account
        if snap_agent_url is not UNSET:
            field_dict["snapAgentUrl"] = snap_agent_url
        if industry_type is not UNSET:
            field_dict["industryType"] = industry_type
        if mapped_meta is not UNSET:
            field_dict["mappedMeta"] = mapped_meta
        if customer_config is not UNSET:
            field_dict["customerConfig"] = customer_config
        if unified_customer_config is not UNSET:
            field_dict["unifiedCustomerConfig"] = unified_customer_config
        if contact_group_id is not UNSET:
            field_dict["contactGroupId"] = contact_group_id
        if auto_renew is not UNSET:
            field_dict["autoRenew"] = auto_renew
        if domain is not UNSET:
            field_dict["domain"] = domain
        if crm_id is not UNSET:
            field_dict["crmId"] = crm_id
        if internal is not UNSET:
            field_dict["internal"] = internal
        if deactivation_date is not UNSET:
            field_dict["deactivationDate"] = deactivation_date
        if updated is not UNSET:
            field_dict["updated"] = updated
        if deleted is not UNSET:
            field_dict["deleted"] = deleted
        if connect_wise_mapping is not UNSET:
            field_dict["connectWiseMapping"] = connect_wise_mapping

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.te_account import TEAccount
        from ..models.te_contact_group import TEContactGroup
        from ..models.te_create_customer_connect_wise_dto import TECreateCustomerConnectWiseDto
        from ..models.te_customer_config import TECustomerConfig
        from ..models.te_customer_mapped_meta_type_0 import TECustomerMappedMetaType0
        from ..models.te_customer_product import TECustomerProduct
        from ..models.te_unified_customer_config import TEUnifiedCustomerConfig

        d = dict(src_dict)
        type_ = check_te_snap_customer_type(d.pop("type"))

        relation_type = check_te_customer_relation_type(d.pop("relationType"))

        id = d.pop("id")

        name = d.pop("name")

        enable_delivery_email = d.pop("enableDeliveryEmail")

        bill_overage = d.pop("billOverage")

        created = isoparse(d.pop("created"))

        customer_products = []
        _customer_products = d.pop("customerProducts", UNSET)
        for customer_products_item_data in _customer_products or []:
            customer_products_item = TECustomerProduct.from_dict(customer_products_item_data)

            customer_products.append(customer_products_item)

        def _parse_connect_wise_company_id(data: object) -> Union[None, Unset, float]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, float], data)

        connect_wise_company_id = _parse_connect_wise_company_id(d.pop("connectWiseCompanyId", UNSET))

        def _parse_connect_wise_note_id(data: object) -> Union[None, Unset, float]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, float], data)

        connect_wise_note_id = _parse_connect_wise_note_id(d.pop("connectWiseNoteId", UNSET))

        def _parse_connect_wise_contact_id(data: object) -> Union[None, Unset, float]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, float], data)

        connect_wise_contact_id = _parse_connect_wise_contact_id(d.pop("connectWiseContactId", UNSET))

        _contact_group = d.pop("contactGroup", UNSET)
        contact_group: Union[Unset, TEContactGroup]
        if isinstance(_contact_group, Unset):
            contact_group = UNSET
        else:
            contact_group = TEContactGroup.from_dict(_contact_group)

        _source = d.pop("source", UNSET)
        source: Union[Unset, TECustomerSourceType]
        if isinstance(_source, Unset):
            source = UNSET
        else:
            source = check_te_customer_source_type(_source)

        def _parse_description(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        description = _parse_description(d.pop("description", UNSET))

        def _parse_account_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        account_id = _parse_account_id(d.pop("accountId", UNSET))

        def _parse_account(data: object) -> Union["TEAccount", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                account_type_1 = TEAccount.from_dict(data)

                return account_type_1
            except:  # noqa: E722
                pass
            return cast(Union["TEAccount", None, Unset], data)

        account = _parse_account(d.pop("account", UNSET))

        def _parse_snap_agent_url(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        snap_agent_url = _parse_snap_agent_url(d.pop("snapAgentUrl", UNSET))

        industry_type = d.pop("industryType", UNSET)

        def _parse_mapped_meta(data: object) -> Union["TECustomerMappedMetaType0", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                mapped_meta_type_0 = TECustomerMappedMetaType0.from_dict(data)

                return mapped_meta_type_0
            except:  # noqa: E722
                pass
            return cast(Union["TECustomerMappedMetaType0", None, Unset], data)

        mapped_meta = _parse_mapped_meta(d.pop("mappedMeta", UNSET))

        _customer_config = d.pop("customerConfig", UNSET)
        customer_config: Union[Unset, TECustomerConfig]
        if isinstance(_customer_config, Unset):
            customer_config = UNSET
        else:
            customer_config = TECustomerConfig.from_dict(_customer_config)

        _unified_customer_config = d.pop("unifiedCustomerConfig", UNSET)
        unified_customer_config: Union[Unset, TEUnifiedCustomerConfig]
        if isinstance(_unified_customer_config, Unset):
            unified_customer_config = UNSET
        else:
            unified_customer_config = TEUnifiedCustomerConfig.from_dict(_unified_customer_config)

        def _parse_contact_group_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        contact_group_id = _parse_contact_group_id(d.pop("contactGroupId", UNSET))

        def _parse_auto_renew(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        auto_renew = _parse_auto_renew(d.pop("autoRenew", UNSET))

        def _parse_domain(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        domain = _parse_domain(d.pop("domain", UNSET))

        def _parse_crm_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        crm_id = _parse_crm_id(d.pop("crmId", UNSET))

        internal = d.pop("internal", UNSET)

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

        _connect_wise_mapping = d.pop("connectWiseMapping", UNSET)
        connect_wise_mapping: Union[Unset, TECreateCustomerConnectWiseDto]
        if isinstance(_connect_wise_mapping, Unset):
            connect_wise_mapping = UNSET
        else:
            connect_wise_mapping = TECreateCustomerConnectWiseDto.from_dict(_connect_wise_mapping)

        te_customer = cls(
            type_=type_,
            relation_type=relation_type,
            id=id,
            name=name,
            enable_delivery_email=enable_delivery_email,
            bill_overage=bill_overage,
            created=created,
            customer_products=customer_products,
            connect_wise_company_id=connect_wise_company_id,
            connect_wise_note_id=connect_wise_note_id,
            connect_wise_contact_id=connect_wise_contact_id,
            contact_group=contact_group,
            source=source,
            description=description,
            account_id=account_id,
            account=account,
            snap_agent_url=snap_agent_url,
            industry_type=industry_type,
            mapped_meta=mapped_meta,
            customer_config=customer_config,
            unified_customer_config=unified_customer_config,
            contact_group_id=contact_group_id,
            auto_renew=auto_renew,
            domain=domain,
            crm_id=crm_id,
            internal=internal,
            deactivation_date=deactivation_date,
            updated=updated,
            deleted=deleted,
            connect_wise_mapping=connect_wise_mapping,
        )

        te_customer.additional_properties = d
        return te_customer

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
