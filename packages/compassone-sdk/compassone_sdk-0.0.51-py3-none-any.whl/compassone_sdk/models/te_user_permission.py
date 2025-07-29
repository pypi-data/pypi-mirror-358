import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.te_user_permission_type import TEUserPermissionType, check_te_user_permission_type
from ..models.te_user_permissions import TEUserPermissions, check_te_user_permissions
from ..types import UNSET, Unset

T = TypeVar("T", bound="TEUserPermission")


@_attrs_define
class TEUserPermission:
    """
    Attributes:
        role (TEUserPermissions):
        user_id (str):
        type_ (Union[Unset, TEUserPermissionType]):
        deleted (Union[None, Unset, datetime.datetime]):
    """

    role: TEUserPermissions
    user_id: str
    type_: Union[Unset, TEUserPermissionType] = UNSET
    deleted: Union[None, Unset, datetime.datetime] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        role: str = self.role

        user_id = self.user_id

        type_: Union[Unset, str] = UNSET
        if not isinstance(self.type_, Unset):
            type_ = self.type_

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
                "role": role,
                "userId": user_id,
            }
        )
        if type_ is not UNSET:
            field_dict["type"] = type_
        if deleted is not UNSET:
            field_dict["deleted"] = deleted

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        role = check_te_user_permissions(d.pop("role"))

        user_id = d.pop("userId")

        _type_ = d.pop("type", UNSET)
        type_: Union[Unset, TEUserPermissionType]
        if isinstance(_type_, Unset):
            type_ = UNSET
        else:
            type_ = check_te_user_permission_type(_type_)

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

        te_user_permission = cls(
            role=role,
            user_id=user_id,
            type_=type_,
            deleted=deleted,
        )

        te_user_permission.additional_properties = d
        return te_user_permission

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
