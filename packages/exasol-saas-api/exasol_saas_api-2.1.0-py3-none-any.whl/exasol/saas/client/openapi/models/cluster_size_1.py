from collections.abc import (
    Generator,
    Mapping,
)
from typing import (
    TYPE_CHECKING,
    Any,
    BinaryIO,
    Optional,
    TextIO,
    TypeVar,
    Union,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import (
    UNSET,
    Unset,
)

T = TypeVar("T", bound="ClusterSize1")


@_attrs_define
class ClusterSize1:
    """
    Attributes:
        size (str):
        price (float):
        vcpu (float):
        ram (float):
        is_default (bool):
        name (str):
        family (Union[Unset, str]):
    """

    size: str
    price: float
    vcpu: float
    ram: float
    is_default: bool
    name: str
    family: Union[Unset, str] = UNSET

    def to_dict(self) -> dict[str, Any]:
        size = self.size

        price = self.price

        vcpu = self.vcpu

        ram = self.ram

        is_default = self.is_default

        name = self.name

        family = self.family

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "size": size,
                "price": price,
                "vcpu": vcpu,
                "ram": ram,
                "isDefault": is_default,
                "name": name,
            }
        )
        if family is not UNSET:
            field_dict["family"] = family

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        size = d.pop("size")

        price = d.pop("price")

        vcpu = d.pop("vcpu")

        ram = d.pop("ram")

        is_default = d.pop("isDefault")

        name = d.pop("name")

        family = d.pop("family", UNSET)

        cluster_size_1 = cls(
            size=size,
            price=price,
            vcpu=vcpu,
            ram=ram,
            is_default=is_default,
            name=name,
            family=family,
        )

        return cluster_size_1
