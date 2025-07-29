import datetime
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define, field as _attrs_field
from dateutil.parser import isoparse

from ..models.incident_group_status import IncidentGroupStatus
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.incident_group_service_schema import IncidentGroupServiceSchema


T = TypeVar("T", bound="IncidentGroupSchema")


@_attrs_define
class IncidentGroupSchema:
    """
    Attributes:
        status (IncidentGroupStatus):
        service (Union['IncidentGroupServiceSchema', None]):
        created_at (datetime.datetime):
        id (Union[None, Unset, int]):
        incident_number (Union[Unset, int]):  Default: 0.
        summary (Union[None, Unset, str]):
        acknowledged_at (Union[None, Unset, datetime.datetime]):
        resolved_at (Union[None, Unset, datetime.datetime]):
        silenced_at (Union[None, Unset, datetime.datetime]):
        last_status_change_at (Union[None, Unset, datetime.datetime]):
    """

    status: IncidentGroupStatus
    service: Union["IncidentGroupServiceSchema", None]
    created_at: datetime.datetime
    id: Union[None, Unset, int] = UNSET
    incident_number: Union[Unset, int] = 0
    summary: Union[None, Unset, str] = UNSET
    acknowledged_at: Union[None, Unset, datetime.datetime] = UNSET
    resolved_at: Union[None, Unset, datetime.datetime] = UNSET
    silenced_at: Union[None, Unset, datetime.datetime] = UNSET
    last_status_change_at: Union[None, Unset, datetime.datetime] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.incident_group_service_schema import IncidentGroupServiceSchema

        status = self.status.value

        service: Union[None, dict[str, Any]]
        if isinstance(self.service, IncidentGroupServiceSchema):
            service = self.service.to_dict()
        else:
            service = self.service

        created_at = self.created_at.isoformat()

        id: Union[None, Unset, int]
        if isinstance(self.id, Unset):
            id = UNSET
        else:
            id = self.id

        incident_number = self.incident_number

        summary: Union[None, Unset, str]
        if isinstance(self.summary, Unset):
            summary = UNSET
        else:
            summary = self.summary

        acknowledged_at: Union[None, Unset, str]
        if isinstance(self.acknowledged_at, Unset):
            acknowledged_at = UNSET
        elif isinstance(self.acknowledged_at, datetime.datetime):
            acknowledged_at = self.acknowledged_at.isoformat()
        else:
            acknowledged_at = self.acknowledged_at

        resolved_at: Union[None, Unset, str]
        if isinstance(self.resolved_at, Unset):
            resolved_at = UNSET
        elif isinstance(self.resolved_at, datetime.datetime):
            resolved_at = self.resolved_at.isoformat()
        else:
            resolved_at = self.resolved_at

        silenced_at: Union[None, Unset, str]
        if isinstance(self.silenced_at, Unset):
            silenced_at = UNSET
        elif isinstance(self.silenced_at, datetime.datetime):
            silenced_at = self.silenced_at.isoformat()
        else:
            silenced_at = self.silenced_at

        last_status_change_at: Union[None, Unset, str]
        if isinstance(self.last_status_change_at, Unset):
            last_status_change_at = UNSET
        elif isinstance(self.last_status_change_at, datetime.datetime):
            last_status_change_at = self.last_status_change_at.isoformat()
        else:
            last_status_change_at = self.last_status_change_at

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "status": status,
                "service": service,
                "created_at": created_at,
            }
        )
        if id is not UNSET:
            field_dict["id"] = id
        if incident_number is not UNSET:
            field_dict["incident_number"] = incident_number
        if summary is not UNSET:
            field_dict["summary"] = summary
        if acknowledged_at is not UNSET:
            field_dict["acknowledged_at"] = acknowledged_at
        if resolved_at is not UNSET:
            field_dict["resolved_at"] = resolved_at
        if silenced_at is not UNSET:
            field_dict["silenced_at"] = silenced_at
        if last_status_change_at is not UNSET:
            field_dict["last_status_change_at"] = last_status_change_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.incident_group_service_schema import IncidentGroupServiceSchema

        d = src_dict.copy()
        status = IncidentGroupStatus(d.pop("status"))

        def _parse_service(data: object) -> Union["IncidentGroupServiceSchema", None]:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                service_type_0 = IncidentGroupServiceSchema.from_dict(data)

                return service_type_0
            except:  # noqa: E722
                pass
            return cast(Union["IncidentGroupServiceSchema", None], data)

        service = _parse_service(d.pop("service"))

        created_at = isoparse(d.pop("created_at"))

        def _parse_id(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        id = _parse_id(d.pop("id", UNSET))

        incident_number = d.pop("incident_number", UNSET)

        def _parse_summary(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        summary = _parse_summary(d.pop("summary", UNSET))

        def _parse_acknowledged_at(data: object) -> Union[None, Unset, datetime.datetime]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                acknowledged_at_type_0 = isoparse(data)

                return acknowledged_at_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, datetime.datetime], data)

        acknowledged_at = _parse_acknowledged_at(d.pop("acknowledged_at", UNSET))

        def _parse_resolved_at(data: object) -> Union[None, Unset, datetime.datetime]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                resolved_at_type_0 = isoparse(data)

                return resolved_at_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, datetime.datetime], data)

        resolved_at = _parse_resolved_at(d.pop("resolved_at", UNSET))

        def _parse_silenced_at(data: object) -> Union[None, Unset, datetime.datetime]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                silenced_at_type_0 = isoparse(data)

                return silenced_at_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, datetime.datetime], data)

        silenced_at = _parse_silenced_at(d.pop("silenced_at", UNSET))

        def _parse_last_status_change_at(data: object) -> Union[None, Unset, datetime.datetime]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                last_status_change_at_type_0 = isoparse(data)

                return last_status_change_at_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, datetime.datetime], data)

        last_status_change_at = _parse_last_status_change_at(d.pop("last_status_change_at", UNSET))

        incident_group_schema = cls(
            status=status,
            service=service,
            created_at=created_at,
            id=id,
            incident_number=incident_number,
            summary=summary,
            acknowledged_at=acknowledged_at,
            resolved_at=resolved_at,
            silenced_at=silenced_at,
            last_status_change_at=last_status_change_at,
        )

        incident_group_schema.additional_properties = d
        return incident_group_schema

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
