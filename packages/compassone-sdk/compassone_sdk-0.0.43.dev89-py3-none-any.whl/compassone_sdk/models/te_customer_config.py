import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="TECustomerConfig")


@_attrs_define
class TECustomerConfig:
    """
    Attributes:
        customer_id (str):
        send_created_processes (bool):
        ransomware_master (bool):
        ransomware_detection (bool):
        ransomware_prevention (bool):
        polling_interval (float):
        windows_defender_enabled (bool):
        created (datetime.datetime):
        windows_defender_event_codes (Union[None, Unset, list[float]]):
        updated (Union[None, Unset, datetime.datetime]):
        deleted (Union[None, Unset, datetime.datetime]):
    """

    customer_id: str
    send_created_processes: bool
    ransomware_master: bool
    ransomware_detection: bool
    ransomware_prevention: bool
    polling_interval: float
    windows_defender_enabled: bool
    created: datetime.datetime
    windows_defender_event_codes: Union[None, Unset, list[float]] = UNSET
    updated: Union[None, Unset, datetime.datetime] = UNSET
    deleted: Union[None, Unset, datetime.datetime] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        customer_id = self.customer_id

        send_created_processes = self.send_created_processes

        ransomware_master = self.ransomware_master

        ransomware_detection = self.ransomware_detection

        ransomware_prevention = self.ransomware_prevention

        polling_interval = self.polling_interval

        windows_defender_enabled = self.windows_defender_enabled

        created = self.created.isoformat()

        windows_defender_event_codes: Union[None, Unset, list[float]]
        if isinstance(self.windows_defender_event_codes, Unset):
            windows_defender_event_codes = UNSET
        elif isinstance(self.windows_defender_event_codes, list):
            windows_defender_event_codes = self.windows_defender_event_codes

        else:
            windows_defender_event_codes = self.windows_defender_event_codes

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
                "customerId": customer_id,
                "sendCreatedProcesses": send_created_processes,
                "ransomwareMaster": ransomware_master,
                "ransomwareDetection": ransomware_detection,
                "ransomwarePrevention": ransomware_prevention,
                "pollingInterval": polling_interval,
                "windowsDefenderEnabled": windows_defender_enabled,
                "created": created,
            }
        )
        if windows_defender_event_codes is not UNSET:
            field_dict["windowsDefenderEventCodes"] = windows_defender_event_codes
        if updated is not UNSET:
            field_dict["updated"] = updated
        if deleted is not UNSET:
            field_dict["deleted"] = deleted

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        customer_id = d.pop("customerId")

        send_created_processes = d.pop("sendCreatedProcesses")

        ransomware_master = d.pop("ransomwareMaster")

        ransomware_detection = d.pop("ransomwareDetection")

        ransomware_prevention = d.pop("ransomwarePrevention")

        polling_interval = d.pop("pollingInterval")

        windows_defender_enabled = d.pop("windowsDefenderEnabled")

        created = isoparse(d.pop("created"))

        def _parse_windows_defender_event_codes(data: object) -> Union[None, Unset, list[float]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                windows_defender_event_codes_type_0 = cast(list[float], data)

                return windows_defender_event_codes_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list[float]], data)

        windows_defender_event_codes = _parse_windows_defender_event_codes(d.pop("windowsDefenderEventCodes", UNSET))

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

        te_customer_config = cls(
            customer_id=customer_id,
            send_created_processes=send_created_processes,
            ransomware_master=ransomware_master,
            ransomware_detection=ransomware_detection,
            ransomware_prevention=ransomware_prevention,
            polling_interval=polling_interval,
            windows_defender_enabled=windows_defender_enabled,
            created=created,
            windows_defender_event_codes=windows_defender_event_codes,
            updated=updated,
            deleted=deleted,
        )

        te_customer_config.additional_properties = d
        return te_customer_config

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
