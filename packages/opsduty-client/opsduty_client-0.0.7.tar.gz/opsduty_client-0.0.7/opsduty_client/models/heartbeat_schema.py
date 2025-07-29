from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define, field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.cron_heartbeat_state_schema import CronHeartbeatStateSchema
    from ..models.interval_heartbeat_state_schema import IntervalHeartbeatStateSchema


T = TypeVar("T", bound="HeartbeatSchema")


@_attrs_define
class HeartbeatSchema:
    """
    Attributes:
        states (list[Union['CronHeartbeatStateSchema', 'IntervalHeartbeatStateSchema']]):
        name (str):
        service (int):
        id (Union[None, Unset, int]):
        public_primary_key (Union[Unset, str]):
        description (Union[None, Unset, str]):  Default: ''.
        link (Union[None, Unset, str]):
        incident_urgency (Union[None, Unset, str]):
        labels (Union[None, Unset, list[Any]]):
    """

    states: list[Union["CronHeartbeatStateSchema", "IntervalHeartbeatStateSchema"]]
    name: str
    service: int
    id: Union[None, Unset, int] = UNSET
    public_primary_key: Union[Unset, str] = UNSET
    description: Union[None, Unset, str] = ""
    link: Union[None, Unset, str] = UNSET
    incident_urgency: Union[None, Unset, str] = UNSET
    labels: Union[None, Unset, list[Any]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.cron_heartbeat_state_schema import CronHeartbeatStateSchema

        states = []
        for states_item_data in self.states:
            states_item: dict[str, Any]
            if isinstance(states_item_data, CronHeartbeatStateSchema):
                states_item = states_item_data.to_dict()
            else:
                states_item = states_item_data.to_dict()

            states.append(states_item)

        name = self.name

        service = self.service

        id: Union[None, Unset, int]
        if isinstance(self.id, Unset):
            id = UNSET
        else:
            id = self.id

        public_primary_key = self.public_primary_key

        description: Union[None, Unset, str]
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        link: Union[None, Unset, str]
        if isinstance(self.link, Unset):
            link = UNSET
        else:
            link = self.link

        incident_urgency: Union[None, Unset, str]
        if isinstance(self.incident_urgency, Unset):
            incident_urgency = UNSET
        else:
            incident_urgency = self.incident_urgency

        labels: Union[None, Unset, list[Any]]
        if isinstance(self.labels, Unset):
            labels = UNSET
        elif isinstance(self.labels, list):
            labels = self.labels

        else:
            labels = self.labels

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "states": states,
                "name": name,
                "service": service,
            }
        )
        if id is not UNSET:
            field_dict["id"] = id
        if public_primary_key is not UNSET:
            field_dict["public_primary_key"] = public_primary_key
        if description is not UNSET:
            field_dict["description"] = description
        if link is not UNSET:
            field_dict["link"] = link
        if incident_urgency is not UNSET:
            field_dict["incident_urgency"] = incident_urgency
        if labels is not UNSET:
            field_dict["labels"] = labels

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.cron_heartbeat_state_schema import CronHeartbeatStateSchema
        from ..models.interval_heartbeat_state_schema import IntervalHeartbeatStateSchema

        d = src_dict.copy()
        states = []
        _states = d.pop("states")
        for states_item_data in _states:

            def _parse_states_item(data: object) -> Union["CronHeartbeatStateSchema", "IntervalHeartbeatStateSchema"]:
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    states_item_type_0 = CronHeartbeatStateSchema.from_dict(data)

                    return states_item_type_0
                except:  # noqa: E722
                    pass
                if not isinstance(data, dict):
                    raise TypeError()
                states_item_type_1 = IntervalHeartbeatStateSchema.from_dict(data)

                return states_item_type_1

            states_item = _parse_states_item(states_item_data)

            states.append(states_item)

        name = d.pop("name")

        service = d.pop("service")

        def _parse_id(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        id = _parse_id(d.pop("id", UNSET))

        public_primary_key = d.pop("public_primary_key", UNSET)

        def _parse_description(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        description = _parse_description(d.pop("description", UNSET))

        def _parse_link(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        link = _parse_link(d.pop("link", UNSET))

        def _parse_incident_urgency(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        incident_urgency = _parse_incident_urgency(d.pop("incident_urgency", UNSET))

        def _parse_labels(data: object) -> Union[None, Unset, list[Any]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                labels_type_0 = cast(list[Any], data)

                return labels_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list[Any]], data)

        labels = _parse_labels(d.pop("labels", UNSET))

        heartbeat_schema = cls(
            states=states,
            name=name,
            service=service,
            id=id,
            public_primary_key=public_primary_key,
            description=description,
            link=link,
            incident_urgency=incident_urgency,
            labels=labels,
        )

        heartbeat_schema.additional_properties = d
        return heartbeat_schema

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
