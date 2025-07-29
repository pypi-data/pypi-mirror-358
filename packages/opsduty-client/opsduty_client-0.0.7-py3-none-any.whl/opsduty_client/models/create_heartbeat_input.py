from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define, field as _attrs_field

from ..models.incident_urgency import IncidentUrgency
from ..types import UNSET, Unset

T = TypeVar("T", bound="CreateHeartbeatInput")


@_attrs_define
class CreateHeartbeatInput:
    """
    Attributes:
        name (str):
        description (str):
        service (int):
        link (Union[None, Unset, str]):
        incident_urgency (Union[IncidentUrgency, None, Unset]):
        labels (Union[Unset, list[str]]):
    """

    name: str
    description: str
    service: int
    link: Union[None, Unset, str] = UNSET
    incident_urgency: Union[IncidentUrgency, None, Unset] = UNSET
    labels: Union[Unset, list[str]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        description = self.description

        service = self.service

        link: Union[None, Unset, str]
        if isinstance(self.link, Unset):
            link = UNSET
        else:
            link = self.link

        incident_urgency: Union[None, Unset, str]
        if isinstance(self.incident_urgency, Unset):
            incident_urgency = UNSET
        elif isinstance(self.incident_urgency, IncidentUrgency):
            incident_urgency = self.incident_urgency.value
        else:
            incident_urgency = self.incident_urgency

        labels: Union[Unset, list[str]] = UNSET
        if not isinstance(self.labels, Unset):
            labels = self.labels

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "description": description,
                "service": service,
            }
        )
        if link is not UNSET:
            field_dict["link"] = link
        if incident_urgency is not UNSET:
            field_dict["incident_urgency"] = incident_urgency
        if labels is not UNSET:
            field_dict["labels"] = labels

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        name = d.pop("name")

        description = d.pop("description")

        service = d.pop("service")

        def _parse_link(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        link = _parse_link(d.pop("link", UNSET))

        def _parse_incident_urgency(data: object) -> Union[IncidentUrgency, None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                incident_urgency_type_0 = IncidentUrgency(data)

                return incident_urgency_type_0
            except:  # noqa: E722
                pass
            return cast(Union[IncidentUrgency, None, Unset], data)

        incident_urgency = _parse_incident_urgency(d.pop("incident_urgency", UNSET))

        labels = cast(list[str], d.pop("labels", UNSET))

        create_heartbeat_input = cls(
            name=name,
            description=description,
            service=service,
            link=link,
            incident_urgency=incident_urgency,
            labels=labels,
        )

        create_heartbeat_input.additional_properties = d
        return create_heartbeat_input

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
