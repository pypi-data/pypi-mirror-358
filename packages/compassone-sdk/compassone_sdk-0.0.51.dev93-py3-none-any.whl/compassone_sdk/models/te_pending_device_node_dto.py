from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.te_pending_device_node_dto_device_subtype import (
    TEPendingDeviceNodeDtoDeviceSubtype,
    check_te_pending_device_node_dto_device_subtype,
)
from ..models.te_pending_device_node_dto_device_type import (
    TEPendingDeviceNodeDtoDeviceType,
    check_te_pending_device_node_dto_device_type,
)
from ..models.te_pending_device_node_dto_operating_system import (
    TEPendingDeviceNodeDtoOperatingSystem,
    check_te_pending_device_node_dto_operating_system,
)
from ..models.te_pending_device_node_dto_vendor import (
    TEPendingDeviceNodeDtoVendor,
    check_te_pending_device_node_dto_vendor,
)
from ..types import UNSET, Unset

T = TypeVar("T", bound="TEPendingDeviceNodeDto")


@_attrs_define
class TEPendingDeviceNodeDto:
    """
    Attributes:
        customer_id (str):
        macs (list[str]):
        cidrs (list[str]):
        canonical_device_id (Union[Unset, str]):
        legacy_device_id (Union[None, Unset, str]):
        domain (Union[None, Unset, str]):
        hostname (Union[Unset, str]):
        device_type (Union[Unset, TEPendingDeviceNodeDtoDeviceType]):
        device_subtype (Union[Unset, TEPendingDeviceNodeDtoDeviceSubtype]):
        operating_system (Union[Unset, TEPendingDeviceNodeDtoOperatingSystem]):
        operating_system_version (Union[Unset, str]):
        vendor (Union[Unset, TEPendingDeviceNodeDtoVendor]):
        chipset_vendor (Union[Unset, str]):
        interface (Union[Unset, str]):
        name (Union[Unset, str]):
        neighbors (Union[Unset, list['TEPendingDeviceNodeDto']]):
    """

    customer_id: str
    macs: list[str]
    cidrs: list[str]
    canonical_device_id: Union[Unset, str] = UNSET
    legacy_device_id: Union[None, Unset, str] = UNSET
    domain: Union[None, Unset, str] = UNSET
    hostname: Union[Unset, str] = UNSET
    device_type: Union[Unset, TEPendingDeviceNodeDtoDeviceType] = UNSET
    device_subtype: Union[Unset, TEPendingDeviceNodeDtoDeviceSubtype] = UNSET
    operating_system: Union[Unset, TEPendingDeviceNodeDtoOperatingSystem] = UNSET
    operating_system_version: Union[Unset, str] = UNSET
    vendor: Union[Unset, TEPendingDeviceNodeDtoVendor] = UNSET
    chipset_vendor: Union[Unset, str] = UNSET
    interface: Union[Unset, str] = UNSET
    name: Union[Unset, str] = UNSET
    neighbors: Union[Unset, list["TEPendingDeviceNodeDto"]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        customer_id = self.customer_id

        macs = self.macs

        cidrs = self.cidrs

        canonical_device_id = self.canonical_device_id

        legacy_device_id: Union[None, Unset, str]
        if isinstance(self.legacy_device_id, Unset):
            legacy_device_id = UNSET
        else:
            legacy_device_id = self.legacy_device_id

        domain: Union[None, Unset, str]
        if isinstance(self.domain, Unset):
            domain = UNSET
        else:
            domain = self.domain

        hostname = self.hostname

        device_type: Union[Unset, str] = UNSET
        if not isinstance(self.device_type, Unset):
            device_type = self.device_type

        device_subtype: Union[Unset, str] = UNSET
        if not isinstance(self.device_subtype, Unset):
            device_subtype = self.device_subtype

        operating_system: Union[Unset, str] = UNSET
        if not isinstance(self.operating_system, Unset):
            operating_system = self.operating_system

        operating_system_version = self.operating_system_version

        vendor: Union[Unset, str] = UNSET
        if not isinstance(self.vendor, Unset):
            vendor = self.vendor

        chipset_vendor = self.chipset_vendor

        interface = self.interface

        name = self.name

        neighbors: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.neighbors, Unset):
            neighbors = []
            for neighbors_item_data in self.neighbors:
                neighbors_item = neighbors_item_data.to_dict()
                neighbors.append(neighbors_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "customerId": customer_id,
                "macs": macs,
                "cidrs": cidrs,
            }
        )
        if canonical_device_id is not UNSET:
            field_dict["canonicalDeviceId"] = canonical_device_id
        if legacy_device_id is not UNSET:
            field_dict["legacyDeviceId"] = legacy_device_id
        if domain is not UNSET:
            field_dict["domain"] = domain
        if hostname is not UNSET:
            field_dict["hostname"] = hostname
        if device_type is not UNSET:
            field_dict["deviceType"] = device_type
        if device_subtype is not UNSET:
            field_dict["deviceSubtype"] = device_subtype
        if operating_system is not UNSET:
            field_dict["operatingSystem"] = operating_system
        if operating_system_version is not UNSET:
            field_dict["operatingSystemVersion"] = operating_system_version
        if vendor is not UNSET:
            field_dict["vendor"] = vendor
        if chipset_vendor is not UNSET:
            field_dict["chipsetVendor"] = chipset_vendor
        if interface is not UNSET:
            field_dict["interface"] = interface
        if name is not UNSET:
            field_dict["name"] = name
        if neighbors is not UNSET:
            field_dict["neighbors"] = neighbors

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        customer_id = d.pop("customerId")

        macs = cast(list[str], d.pop("macs"))

        cidrs = cast(list[str], d.pop("cidrs"))

        canonical_device_id = d.pop("canonicalDeviceId", UNSET)

        def _parse_legacy_device_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        legacy_device_id = _parse_legacy_device_id(d.pop("legacyDeviceId", UNSET))

        def _parse_domain(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        domain = _parse_domain(d.pop("domain", UNSET))

        hostname = d.pop("hostname", UNSET)

        _device_type = d.pop("deviceType", UNSET)
        device_type: Union[Unset, TEPendingDeviceNodeDtoDeviceType]
        if isinstance(_device_type, Unset):
            device_type = UNSET
        else:
            device_type = check_te_pending_device_node_dto_device_type(_device_type)

        _device_subtype = d.pop("deviceSubtype", UNSET)
        device_subtype: Union[Unset, TEPendingDeviceNodeDtoDeviceSubtype]
        if isinstance(_device_subtype, Unset):
            device_subtype = UNSET
        else:
            device_subtype = check_te_pending_device_node_dto_device_subtype(_device_subtype)

        _operating_system = d.pop("operatingSystem", UNSET)
        operating_system: Union[Unset, TEPendingDeviceNodeDtoOperatingSystem]
        if isinstance(_operating_system, Unset):
            operating_system = UNSET
        else:
            operating_system = check_te_pending_device_node_dto_operating_system(_operating_system)

        operating_system_version = d.pop("operatingSystemVersion", UNSET)

        _vendor = d.pop("vendor", UNSET)
        vendor: Union[Unset, TEPendingDeviceNodeDtoVendor]
        if isinstance(_vendor, Unset):
            vendor = UNSET
        else:
            vendor = check_te_pending_device_node_dto_vendor(_vendor)

        chipset_vendor = d.pop("chipsetVendor", UNSET)

        interface = d.pop("interface", UNSET)

        name = d.pop("name", UNSET)

        neighbors = []
        _neighbors = d.pop("neighbors", UNSET)
        for neighbors_item_data in _neighbors or []:
            neighbors_item = TEPendingDeviceNodeDto.from_dict(neighbors_item_data)

            neighbors.append(neighbors_item)

        te_pending_device_node_dto = cls(
            customer_id=customer_id,
            macs=macs,
            cidrs=cidrs,
            canonical_device_id=canonical_device_id,
            legacy_device_id=legacy_device_id,
            domain=domain,
            hostname=hostname,
            device_type=device_type,
            device_subtype=device_subtype,
            operating_system=operating_system,
            operating_system_version=operating_system_version,
            vendor=vendor,
            chipset_vendor=chipset_vendor,
            interface=interface,
            name=name,
            neighbors=neighbors,
        )

        te_pending_device_node_dto.additional_properties = d
        return te_pending_device_node_dto

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
