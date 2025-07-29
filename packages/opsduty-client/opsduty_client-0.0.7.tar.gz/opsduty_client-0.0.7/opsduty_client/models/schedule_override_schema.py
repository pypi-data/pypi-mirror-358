import datetime
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define, field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.schedule_override_user_schema import ScheduleOverrideUserSchema


T = TypeVar("T", bound="ScheduleOverrideSchema")


@_attrs_define
class ScheduleOverrideSchema:
    """
    Attributes:
        user (ScheduleOverrideUserSchema):
        start (datetime.datetime):
        end (datetime.datetime):
        id (Union[None, Unset, int]):
    """

    user: "ScheduleOverrideUserSchema"
    start: datetime.datetime
    end: datetime.datetime
    id: Union[None, Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        user = self.user.to_dict()

        start = self.start.isoformat()

        end = self.end.isoformat()

        id: Union[None, Unset, int]
        if isinstance(self.id, Unset):
            id = UNSET
        else:
            id = self.id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "user": user,
                "start": start,
                "end": end,
            }
        )
        if id is not UNSET:
            field_dict["id"] = id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.schedule_override_user_schema import ScheduleOverrideUserSchema

        d = src_dict.copy()
        user = ScheduleOverrideUserSchema.from_dict(d.pop("user"))

        start = isoparse(d.pop("start"))

        end = isoparse(d.pop("end"))

        def _parse_id(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        id = _parse_id(d.pop("id", UNSET))

        schedule_override_schema = cls(
            user=user,
            start=start,
            end=end,
            id=id,
        )

        schedule_override_schema.additional_properties = d
        return schedule_override_schema

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
