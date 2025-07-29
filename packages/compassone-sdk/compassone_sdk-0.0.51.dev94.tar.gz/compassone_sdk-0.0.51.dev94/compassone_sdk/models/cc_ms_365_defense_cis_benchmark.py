import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.cc_ms_365_defense_cis_benchmark_status import (
    CCMs365DefenseCisBenchmarkStatus,
    check_cc_ms_365_defense_cis_benchmark_status,
)
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.cc_ms_365_defense_cis_benchmark_metadata import CCMs365DefenseCisBenchmarkMetadata


T = TypeVar("T", bound="CCMs365DefenseCisBenchmark")


@_attrs_define
class CCMs365DefenseCisBenchmark:
    """
    Attributes:
        id (str):
        ms_365_defense_cis_master_benchmark_id (str):
        ms_365_defense_package_id (str):
        status (CCMs365DefenseCisBenchmarkStatus):
        created (datetime.datetime):
        updated (Union[None, Unset, datetime.datetime]):
        deleted (Union[None, Unset, datetime.datetime]):
        metadata (Union[Unset, list['CCMs365DefenseCisBenchmarkMetadata']]):
    """

    id: str
    ms_365_defense_cis_master_benchmark_id: str
    ms_365_defense_package_id: str
    status: CCMs365DefenseCisBenchmarkStatus
    created: datetime.datetime
    updated: Union[None, Unset, datetime.datetime] = UNSET
    deleted: Union[None, Unset, datetime.datetime] = UNSET
    metadata: Union[Unset, list["CCMs365DefenseCisBenchmarkMetadata"]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        ms_365_defense_cis_master_benchmark_id = self.ms_365_defense_cis_master_benchmark_id

        ms_365_defense_package_id = self.ms_365_defense_package_id

        status: str = self.status

        created = self.created.isoformat()

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

        metadata: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = []
            for metadata_item_data in self.metadata:
                metadata_item = metadata_item_data.to_dict()
                metadata.append(metadata_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "ms365DefenseCisMasterBenchmarkId": ms_365_defense_cis_master_benchmark_id,
                "ms365DefensePackageId": ms_365_defense_package_id,
                "status": status,
                "created": created,
            }
        )
        if updated is not UNSET:
            field_dict["updated"] = updated
        if deleted is not UNSET:
            field_dict["deleted"] = deleted
        if metadata is not UNSET:
            field_dict["metadata"] = metadata

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.cc_ms_365_defense_cis_benchmark_metadata import CCMs365DefenseCisBenchmarkMetadata

        d = dict(src_dict)
        id = d.pop("id")

        ms_365_defense_cis_master_benchmark_id = d.pop("ms365DefenseCisMasterBenchmarkId")

        ms_365_defense_package_id = d.pop("ms365DefensePackageId")

        status = check_cc_ms_365_defense_cis_benchmark_status(d.pop("status"))

        created = isoparse(d.pop("created"))

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

        metadata = []
        _metadata = d.pop("metadata", UNSET)
        for metadata_item_data in _metadata or []:
            metadata_item = CCMs365DefenseCisBenchmarkMetadata.from_dict(metadata_item_data)

            metadata.append(metadata_item)

        cc_ms_365_defense_cis_benchmark = cls(
            id=id,
            ms_365_defense_cis_master_benchmark_id=ms_365_defense_cis_master_benchmark_id,
            ms_365_defense_package_id=ms_365_defense_package_id,
            status=status,
            created=created,
            updated=updated,
            deleted=deleted,
            metadata=metadata,
        )

        cc_ms_365_defense_cis_benchmark.additional_properties = d
        return cc_ms_365_defense_cis_benchmark

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
