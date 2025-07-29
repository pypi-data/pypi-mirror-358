import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.te_account import TEAccount
    from ..models.te_customer import TECustomer
    from ..models.te_invite import TEInvite
    from ..models.te_user_permission import TEUserPermission


T = TypeVar("T", bound="TEUser")


@_attrs_define
class TEUser:
    """
    Attributes:
        id (str):
        email (str):
        name (str):
        created (datetime.datetime):
        roles (Union[Unset, list['TEUserPermission']]):
        invites (Union[Unset, list['TEInvite']]):
        external_id (Union[None, Unset, str]):
        nickname (Union[None, Unset, str]):
        picture (Union[None, Unset, str]):
        account_id (Union[None, Unset, str]):
        assigned_accounts (Union[None, Unset, list['TEAccount']]):
        assigned_customers (Union[None, Unset, list['TECustomer']]):
        activation_date (Union[None, Unset, datetime.datetime]):
        updated (Union[None, Unset, datetime.datetime]):
        deleted (Union[None, Unset, datetime.datetime]):
    """

    id: str
    email: str
    name: str
    created: datetime.datetime
    roles: Union[Unset, list["TEUserPermission"]] = UNSET
    invites: Union[Unset, list["TEInvite"]] = UNSET
    external_id: Union[None, Unset, str] = UNSET
    nickname: Union[None, Unset, str] = UNSET
    picture: Union[None, Unset, str] = UNSET
    account_id: Union[None, Unset, str] = UNSET
    assigned_accounts: Union[None, Unset, list["TEAccount"]] = UNSET
    assigned_customers: Union[None, Unset, list["TECustomer"]] = UNSET
    activation_date: Union[None, Unset, datetime.datetime] = UNSET
    updated: Union[None, Unset, datetime.datetime] = UNSET
    deleted: Union[None, Unset, datetime.datetime] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        email = self.email

        name = self.name

        created = self.created.isoformat()

        roles: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.roles, Unset):
            roles = []
            for roles_item_data in self.roles:
                roles_item = roles_item_data.to_dict()
                roles.append(roles_item)

        invites: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.invites, Unset):
            invites = []
            for invites_item_data in self.invites:
                invites_item = invites_item_data.to_dict()
                invites.append(invites_item)

        external_id: Union[None, Unset, str]
        if isinstance(self.external_id, Unset):
            external_id = UNSET
        else:
            external_id = self.external_id

        nickname: Union[None, Unset, str]
        if isinstance(self.nickname, Unset):
            nickname = UNSET
        else:
            nickname = self.nickname

        picture: Union[None, Unset, str]
        if isinstance(self.picture, Unset):
            picture = UNSET
        else:
            picture = self.picture

        account_id: Union[None, Unset, str]
        if isinstance(self.account_id, Unset):
            account_id = UNSET
        else:
            account_id = self.account_id

        assigned_accounts: Union[None, Unset, list[dict[str, Any]]]
        if isinstance(self.assigned_accounts, Unset):
            assigned_accounts = UNSET
        elif isinstance(self.assigned_accounts, list):
            assigned_accounts = []
            for assigned_accounts_type_0_item_data in self.assigned_accounts:
                assigned_accounts_type_0_item = assigned_accounts_type_0_item_data.to_dict()
                assigned_accounts.append(assigned_accounts_type_0_item)

        else:
            assigned_accounts = self.assigned_accounts

        assigned_customers: Union[None, Unset, list[dict[str, Any]]]
        if isinstance(self.assigned_customers, Unset):
            assigned_customers = UNSET
        elif isinstance(self.assigned_customers, list):
            assigned_customers = []
            for assigned_customers_type_0_item_data in self.assigned_customers:
                assigned_customers_type_0_item = assigned_customers_type_0_item_data.to_dict()
                assigned_customers.append(assigned_customers_type_0_item)

        else:
            assigned_customers = self.assigned_customers

        activation_date: Union[None, Unset, str]
        if isinstance(self.activation_date, Unset):
            activation_date = UNSET
        elif isinstance(self.activation_date, datetime.datetime):
            activation_date = self.activation_date.isoformat()
        else:
            activation_date = self.activation_date

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
                "email": email,
                "name": name,
                "created": created,
            }
        )
        if roles is not UNSET:
            field_dict["roles"] = roles
        if invites is not UNSET:
            field_dict["invites"] = invites
        if external_id is not UNSET:
            field_dict["externalId"] = external_id
        if nickname is not UNSET:
            field_dict["nickname"] = nickname
        if picture is not UNSET:
            field_dict["picture"] = picture
        if account_id is not UNSET:
            field_dict["accountId"] = account_id
        if assigned_accounts is not UNSET:
            field_dict["assignedAccounts"] = assigned_accounts
        if assigned_customers is not UNSET:
            field_dict["assignedCustomers"] = assigned_customers
        if activation_date is not UNSET:
            field_dict["activationDate"] = activation_date
        if updated is not UNSET:
            field_dict["updated"] = updated
        if deleted is not UNSET:
            field_dict["deleted"] = deleted

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.te_account import TEAccount
        from ..models.te_customer import TECustomer
        from ..models.te_invite import TEInvite
        from ..models.te_user_permission import TEUserPermission

        d = dict(src_dict)
        id = d.pop("id")

        email = d.pop("email")

        name = d.pop("name")

        created = isoparse(d.pop("created"))

        roles = []
        _roles = d.pop("roles", UNSET)
        for roles_item_data in _roles or []:
            roles_item = TEUserPermission.from_dict(roles_item_data)

            roles.append(roles_item)

        invites = []
        _invites = d.pop("invites", UNSET)
        for invites_item_data in _invites or []:
            invites_item = TEInvite.from_dict(invites_item_data)

            invites.append(invites_item)

        def _parse_external_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        external_id = _parse_external_id(d.pop("externalId", UNSET))

        def _parse_nickname(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        nickname = _parse_nickname(d.pop("nickname", UNSET))

        def _parse_picture(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        picture = _parse_picture(d.pop("picture", UNSET))

        def _parse_account_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        account_id = _parse_account_id(d.pop("accountId", UNSET))

        def _parse_assigned_accounts(data: object) -> Union[None, Unset, list["TEAccount"]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                assigned_accounts_type_0 = []
                _assigned_accounts_type_0 = data
                for assigned_accounts_type_0_item_data in _assigned_accounts_type_0:
                    assigned_accounts_type_0_item = TEAccount.from_dict(assigned_accounts_type_0_item_data)

                    assigned_accounts_type_0.append(assigned_accounts_type_0_item)

                return assigned_accounts_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list["TEAccount"]], data)

        assigned_accounts = _parse_assigned_accounts(d.pop("assignedAccounts", UNSET))

        def _parse_assigned_customers(data: object) -> Union[None, Unset, list["TECustomer"]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                assigned_customers_type_0 = []
                _assigned_customers_type_0 = data
                for assigned_customers_type_0_item_data in _assigned_customers_type_0:
                    assigned_customers_type_0_item = TECustomer.from_dict(assigned_customers_type_0_item_data)

                    assigned_customers_type_0.append(assigned_customers_type_0_item)

                return assigned_customers_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list["TECustomer"]], data)

        assigned_customers = _parse_assigned_customers(d.pop("assignedCustomers", UNSET))

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

        te_user = cls(
            id=id,
            email=email,
            name=name,
            created=created,
            roles=roles,
            invites=invites,
            external_id=external_id,
            nickname=nickname,
            picture=picture,
            account_id=account_id,
            assigned_accounts=assigned_accounts,
            assigned_customers=assigned_customers,
            activation_date=activation_date,
            updated=updated,
            deleted=deleted,
        )

        te_user.additional_properties = d
        return te_user

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
