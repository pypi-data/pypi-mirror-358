import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.cc_ms_365_defense_master_event import CCMs365DefenseMasterEvent


T = TypeVar("T", bound="CCMs365DefenseEvent")


@_attrs_define
class CCMs365DefenseEvent:
    """
    Attributes:
        id (str):
        notify (bool):
        ms_365_defense_package_id (str):
        ms_365_defense_master_event_id (str):
        ms_365_defense_master_event (CCMs365DefenseMasterEvent):
        created (datetime.datetime):
        suppression_rule_id (Union[None, Unset, str]):
        updated (Union[None, Unset, datetime.datetime]):
        deleted (Union[None, Unset, datetime.datetime]):
        critical (Union[Unset, bool]):
    """

    id: str
    notify: bool
    ms_365_defense_package_id: str
    ms_365_defense_master_event_id: str
    ms_365_defense_master_event: "CCMs365DefenseMasterEvent"
    created: datetime.datetime
    suppression_rule_id: Union[None, Unset, str] = UNSET
    updated: Union[None, Unset, datetime.datetime] = UNSET
    deleted: Union[None, Unset, datetime.datetime] = UNSET
    critical: Union[Unset, bool] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        notify = self.notify

        ms_365_defense_package_id = self.ms_365_defense_package_id

        ms_365_defense_master_event_id = self.ms_365_defense_master_event_id

        ms_365_defense_master_event = self.ms_365_defense_master_event.to_dict()

        created = self.created.isoformat()

        suppression_rule_id: Union[None, Unset, str]
        if isinstance(self.suppression_rule_id, Unset):
            suppression_rule_id = UNSET
        else:
            suppression_rule_id = self.suppression_rule_id

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

        critical = self.critical

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "notify": notify,
                "ms365DefensePackageId": ms_365_defense_package_id,
                "ms365DefenseMasterEventId": ms_365_defense_master_event_id,
                "ms365DefenseMasterEvent": ms_365_defense_master_event,
                "created": created,
            }
        )
        if suppression_rule_id is not UNSET:
            field_dict["suppressionRuleId"] = suppression_rule_id
        if updated is not UNSET:
            field_dict["updated"] = updated
        if deleted is not UNSET:
            field_dict["deleted"] = deleted
        if critical is not UNSET:
            field_dict["critical"] = critical

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.cc_ms_365_defense_master_event import CCMs365DefenseMasterEvent

        d = dict(src_dict)
        id = d.pop("id")

        notify = d.pop("notify")

        ms_365_defense_package_id = d.pop("ms365DefensePackageId")

        ms_365_defense_master_event_id = d.pop("ms365DefenseMasterEventId")

        ms_365_defense_master_event = CCMs365DefenseMasterEvent.from_dict(d.pop("ms365DefenseMasterEvent"))

        created = isoparse(d.pop("created"))

        def _parse_suppression_rule_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        suppression_rule_id = _parse_suppression_rule_id(d.pop("suppressionRuleId", UNSET))

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

        critical = d.pop("critical", UNSET)

        cc_ms_365_defense_event = cls(
            id=id,
            notify=notify,
            ms_365_defense_package_id=ms_365_defense_package_id,
            ms_365_defense_master_event_id=ms_365_defense_master_event_id,
            ms_365_defense_master_event=ms_365_defense_master_event,
            created=created,
            suppression_rule_id=suppression_rule_id,
            updated=updated,
            deleted=deleted,
            critical=critical,
        )

        cc_ms_365_defense_event.additional_properties = d
        return cc_ms_365_defense_event

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
