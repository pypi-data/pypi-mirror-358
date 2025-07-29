import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.te_customer_product_product_meta_type_0 import TECustomerProductProductMetaType0
    from ..models.te_product import TEProduct


T = TypeVar("T", bound="TECustomerProduct")


@_attrs_define
class TECustomerProduct:
    """
    Attributes:
        id (str): This property should not be used. Use customerId + productId instead
        customer_id (str):
        expires (datetime.datetime):
        trial (bool):
        product_id (str):
        is_bulk (bool):
        is_standalone (bool):
        created (datetime.datetime):
        initial_min_commitment (Union[None, Unset, float]): Use initialMinCommit instead
        account_id (Union[None, Unset, str]):
        initial_min_commit (Union[None, Unset, float]):
        min_commit_updated (Union[None, Unset, datetime.datetime]):
        parent_product_id (Union[None, Unset, str]):
        quantity (Union[None, Unset, float]):
        paid_converted_date (Union[None, Unset, datetime.datetime]):
        product (Union['TEProduct', None, Unset]):
        product_meta (Union['TECustomerProductProductMetaType0', None, Unset]):
        deactivation_date (Union[None, Unset, datetime.datetime]):
        updated (Union[None, Unset, datetime.datetime]):
        deleted (Union[None, Unset, datetime.datetime]):
    """

    id: str
    customer_id: str
    expires: datetime.datetime
    trial: bool
    product_id: str
    is_bulk: bool
    is_standalone: bool
    created: datetime.datetime
    initial_min_commitment: Union[None, Unset, float] = UNSET
    account_id: Union[None, Unset, str] = UNSET
    initial_min_commit: Union[None, Unset, float] = UNSET
    min_commit_updated: Union[None, Unset, datetime.datetime] = UNSET
    parent_product_id: Union[None, Unset, str] = UNSET
    quantity: Union[None, Unset, float] = UNSET
    paid_converted_date: Union[None, Unset, datetime.datetime] = UNSET
    product: Union["TEProduct", None, Unset] = UNSET
    product_meta: Union["TECustomerProductProductMetaType0", None, Unset] = UNSET
    deactivation_date: Union[None, Unset, datetime.datetime] = UNSET
    updated: Union[None, Unset, datetime.datetime] = UNSET
    deleted: Union[None, Unset, datetime.datetime] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.te_customer_product_product_meta_type_0 import TECustomerProductProductMetaType0
        from ..models.te_product import TEProduct

        id = self.id

        customer_id = self.customer_id

        expires = self.expires.isoformat()

        trial = self.trial

        product_id = self.product_id

        is_bulk = self.is_bulk

        is_standalone = self.is_standalone

        created = self.created.isoformat()

        initial_min_commitment: Union[None, Unset, float]
        if isinstance(self.initial_min_commitment, Unset):
            initial_min_commitment = UNSET
        else:
            initial_min_commitment = self.initial_min_commitment

        account_id: Union[None, Unset, str]
        if isinstance(self.account_id, Unset):
            account_id = UNSET
        else:
            account_id = self.account_id

        initial_min_commit: Union[None, Unset, float]
        if isinstance(self.initial_min_commit, Unset):
            initial_min_commit = UNSET
        else:
            initial_min_commit = self.initial_min_commit

        min_commit_updated: Union[None, Unset, str]
        if isinstance(self.min_commit_updated, Unset):
            min_commit_updated = UNSET
        elif isinstance(self.min_commit_updated, datetime.datetime):
            min_commit_updated = self.min_commit_updated.isoformat()
        else:
            min_commit_updated = self.min_commit_updated

        parent_product_id: Union[None, Unset, str]
        if isinstance(self.parent_product_id, Unset):
            parent_product_id = UNSET
        else:
            parent_product_id = self.parent_product_id

        quantity: Union[None, Unset, float]
        if isinstance(self.quantity, Unset):
            quantity = UNSET
        else:
            quantity = self.quantity

        paid_converted_date: Union[None, Unset, str]
        if isinstance(self.paid_converted_date, Unset):
            paid_converted_date = UNSET
        elif isinstance(self.paid_converted_date, datetime.datetime):
            paid_converted_date = self.paid_converted_date.isoformat()
        else:
            paid_converted_date = self.paid_converted_date

        product: Union[None, Unset, dict[str, Any]]
        if isinstance(self.product, Unset):
            product = UNSET
        elif isinstance(self.product, TEProduct):
            product = self.product.to_dict()
        else:
            product = self.product

        product_meta: Union[None, Unset, dict[str, Any]]
        if isinstance(self.product_meta, Unset):
            product_meta = UNSET
        elif isinstance(self.product_meta, TECustomerProductProductMetaType0):
            product_meta = self.product_meta.to_dict()
        else:
            product_meta = self.product_meta

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
                "id": id,
                "customerId": customer_id,
                "expires": expires,
                "trial": trial,
                "productId": product_id,
                "isBulk": is_bulk,
                "isStandalone": is_standalone,
                "created": created,
            }
        )
        if initial_min_commitment is not UNSET:
            field_dict["initialMinCommitment"] = initial_min_commitment
        if account_id is not UNSET:
            field_dict["accountId"] = account_id
        if initial_min_commit is not UNSET:
            field_dict["initialMinCommit"] = initial_min_commit
        if min_commit_updated is not UNSET:
            field_dict["minCommitUpdated"] = min_commit_updated
        if parent_product_id is not UNSET:
            field_dict["parentProductId"] = parent_product_id
        if quantity is not UNSET:
            field_dict["quantity"] = quantity
        if paid_converted_date is not UNSET:
            field_dict["paidConvertedDate"] = paid_converted_date
        if product is not UNSET:
            field_dict["product"] = product
        if product_meta is not UNSET:
            field_dict["productMeta"] = product_meta
        if deactivation_date is not UNSET:
            field_dict["deactivationDate"] = deactivation_date
        if updated is not UNSET:
            field_dict["updated"] = updated
        if deleted is not UNSET:
            field_dict["deleted"] = deleted

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.te_customer_product_product_meta_type_0 import TECustomerProductProductMetaType0
        from ..models.te_product import TEProduct

        d = dict(src_dict)
        id = d.pop("id")

        customer_id = d.pop("customerId")

        expires = isoparse(d.pop("expires"))

        trial = d.pop("trial")

        product_id = d.pop("productId")

        is_bulk = d.pop("isBulk")

        is_standalone = d.pop("isStandalone")

        created = isoparse(d.pop("created"))

        def _parse_initial_min_commitment(data: object) -> Union[None, Unset, float]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, float], data)

        initial_min_commitment = _parse_initial_min_commitment(d.pop("initialMinCommitment", UNSET))

        def _parse_account_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        account_id = _parse_account_id(d.pop("accountId", UNSET))

        def _parse_initial_min_commit(data: object) -> Union[None, Unset, float]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, float], data)

        initial_min_commit = _parse_initial_min_commit(d.pop("initialMinCommit", UNSET))

        def _parse_min_commit_updated(data: object) -> Union[None, Unset, datetime.datetime]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                min_commit_updated_type_0 = isoparse(data)

                return min_commit_updated_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, datetime.datetime], data)

        min_commit_updated = _parse_min_commit_updated(d.pop("minCommitUpdated", UNSET))

        def _parse_parent_product_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        parent_product_id = _parse_parent_product_id(d.pop("parentProductId", UNSET))

        def _parse_quantity(data: object) -> Union[None, Unset, float]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, float], data)

        quantity = _parse_quantity(d.pop("quantity", UNSET))

        def _parse_paid_converted_date(data: object) -> Union[None, Unset, datetime.datetime]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                paid_converted_date_type_0 = isoparse(data)

                return paid_converted_date_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, datetime.datetime], data)

        paid_converted_date = _parse_paid_converted_date(d.pop("paidConvertedDate", UNSET))

        def _parse_product(data: object) -> Union["TEProduct", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                product_type_1 = TEProduct.from_dict(data)

                return product_type_1
            except:  # noqa: E722
                pass
            return cast(Union["TEProduct", None, Unset], data)

        product = _parse_product(d.pop("product", UNSET))

        def _parse_product_meta(data: object) -> Union["TECustomerProductProductMetaType0", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                product_meta_type_0 = TECustomerProductProductMetaType0.from_dict(data)

                return product_meta_type_0
            except:  # noqa: E722
                pass
            return cast(Union["TECustomerProductProductMetaType0", None, Unset], data)

        product_meta = _parse_product_meta(d.pop("productMeta", UNSET))

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

        te_customer_product = cls(
            id=id,
            customer_id=customer_id,
            expires=expires,
            trial=trial,
            product_id=product_id,
            is_bulk=is_bulk,
            is_standalone=is_standalone,
            created=created,
            initial_min_commitment=initial_min_commitment,
            account_id=account_id,
            initial_min_commit=initial_min_commit,
            min_commit_updated=min_commit_updated,
            parent_product_id=parent_product_id,
            quantity=quantity,
            paid_converted_date=paid_converted_date,
            product=product,
            product_meta=product_meta,
            deactivation_date=deactivation_date,
            updated=updated,
            deleted=deleted,
        )

        te_customer_product.additional_properties = d
        return te_customer_product

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
