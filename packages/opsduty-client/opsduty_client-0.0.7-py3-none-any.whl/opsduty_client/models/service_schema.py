from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define, field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ServiceSchema")


@_attrs_define
class ServiceSchema:
    """
    Attributes:
        name (str):
        id (Union[None, Unset, int]):
        description (Union[None, Unset, str]):
        service_type (Union[Unset, str]):  Default: 'technical'.
        routing_key (Union[Unset, str]):
    """

    name: str
    id: Union[None, Unset, int] = UNSET
    description: Union[None, Unset, str] = UNSET
    service_type: Union[Unset, str] = "technical"
    routing_key: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        id: Union[None, Unset, int]
        if isinstance(self.id, Unset):
            id = UNSET
        else:
            id = self.id

        description: Union[None, Unset, str]
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        service_type = self.service_type

        routing_key = self.routing_key

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
            }
        )
        if id is not UNSET:
            field_dict["id"] = id
        if description is not UNSET:
            field_dict["description"] = description
        if service_type is not UNSET:
            field_dict["service_type"] = service_type
        if routing_key is not UNSET:
            field_dict["routing_key"] = routing_key

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        name = d.pop("name")

        def _parse_id(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        id = _parse_id(d.pop("id", UNSET))

        def _parse_description(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        description = _parse_description(d.pop("description", UNSET))

        service_type = d.pop("service_type", UNSET)

        routing_key = d.pop("routing_key", UNSET)

        service_schema = cls(
            name=name,
            id=id,
            description=description,
            service_type=service_type,
            routing_key=routing_key,
        )

        service_schema.additional_properties = d
        return service_schema

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
