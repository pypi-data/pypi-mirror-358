import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.te_product import TEProduct


T = TypeVar("T", bound="TEBillingContract")


@_attrs_define
class TEBillingContract:
    """
    Attributes:
        start_date (datetime.datetime): Date the contract starts.
        end_date (datetime.datetime): Date the contract ends.
        billing_start_date (datetime.datetime): Date the billing starts in Stripe and the account is charged.
        id (str):
        account_id (str):
        product_id (str):
        price_id (str):
        device_commit (float):
        auto_renew (bool):
        exclude_device_overage (bool):
        exclude_user_overage (bool):
        created (datetime.datetime):
        void_date (Union[None, Unset, datetime.datetime]): When changes are made to a contract, the previous one is
            voided. If null the contract is considered active.
        product (Union['TEProduct', None, Unset]):
        updated (Union[None, Unset, datetime.datetime]):
        deleted (Union[None, Unset, datetime.datetime]):
    """

    start_date: datetime.datetime
    end_date: datetime.datetime
    billing_start_date: datetime.datetime
    id: str
    account_id: str
    product_id: str
    price_id: str
    device_commit: float
    auto_renew: bool
    exclude_device_overage: bool
    exclude_user_overage: bool
    created: datetime.datetime
    void_date: Union[None, Unset, datetime.datetime] = UNSET
    product: Union["TEProduct", None, Unset] = UNSET
    updated: Union[None, Unset, datetime.datetime] = UNSET
    deleted: Union[None, Unset, datetime.datetime] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.te_product import TEProduct

        start_date = self.start_date.isoformat()

        end_date = self.end_date.isoformat()

        billing_start_date = self.billing_start_date.isoformat()

        id = self.id

        account_id = self.account_id

        product_id = self.product_id

        price_id = self.price_id

        device_commit = self.device_commit

        auto_renew = self.auto_renew

        exclude_device_overage = self.exclude_device_overage

        exclude_user_overage = self.exclude_user_overage

        created = self.created.isoformat()

        void_date: Union[None, Unset, str]
        if isinstance(self.void_date, Unset):
            void_date = UNSET
        elif isinstance(self.void_date, datetime.datetime):
            void_date = self.void_date.isoformat()
        else:
            void_date = self.void_date

        product: Union[None, Unset, dict[str, Any]]
        if isinstance(self.product, Unset):
            product = UNSET
        elif isinstance(self.product, TEProduct):
            product = self.product.to_dict()
        else:
            product = self.product

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
                "startDate": start_date,
                "endDate": end_date,
                "billingStartDate": billing_start_date,
                "id": id,
                "accountId": account_id,
                "productId": product_id,
                "priceId": price_id,
                "deviceCommit": device_commit,
                "autoRenew": auto_renew,
                "excludeDeviceOverage": exclude_device_overage,
                "excludeUserOverage": exclude_user_overage,
                "created": created,
            }
        )
        if void_date is not UNSET:
            field_dict["voidDate"] = void_date
        if product is not UNSET:
            field_dict["product"] = product
        if updated is not UNSET:
            field_dict["updated"] = updated
        if deleted is not UNSET:
            field_dict["deleted"] = deleted

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.te_product import TEProduct

        d = dict(src_dict)
        start_date = isoparse(d.pop("startDate"))

        end_date = isoparse(d.pop("endDate"))

        billing_start_date = isoparse(d.pop("billingStartDate"))

        id = d.pop("id")

        account_id = d.pop("accountId")

        product_id = d.pop("productId")

        price_id = d.pop("priceId")

        device_commit = d.pop("deviceCommit")

        auto_renew = d.pop("autoRenew")

        exclude_device_overage = d.pop("excludeDeviceOverage")

        exclude_user_overage = d.pop("excludeUserOverage")

        created = isoparse(d.pop("created"))

        def _parse_void_date(data: object) -> Union[None, Unset, datetime.datetime]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                void_date_type_0 = isoparse(data)

                return void_date_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, datetime.datetime], data)

        void_date = _parse_void_date(d.pop("voidDate", UNSET))

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

        te_billing_contract = cls(
            start_date=start_date,
            end_date=end_date,
            billing_start_date=billing_start_date,
            id=id,
            account_id=account_id,
            product_id=product_id,
            price_id=price_id,
            device_commit=device_commit,
            auto_renew=auto_renew,
            exclude_device_overage=exclude_device_overage,
            exclude_user_overage=exclude_user_overage,
            created=created,
            void_date=void_date,
            product=product,
            updated=updated,
            deleted=deleted,
        )

        te_billing_contract.additional_properties = d
        return te_billing_contract

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
