import datetime
from typing import Any, TypeVar

from attrs import define as _attrs_define, field as _attrs_field
from dateutil.parser import isoparse

T = TypeVar("T", bound="ScheduleOverrideInputSchema")


@_attrs_define
class ScheduleOverrideInputSchema:
    """
    Attributes:
        user_id (int):
        start (datetime.datetime):
        end (datetime.datetime):
    """

    user_id: int
    start: datetime.datetime
    end: datetime.datetime
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        user_id = self.user_id

        start = self.start.isoformat()

        end = self.end.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "user_id": user_id,
                "start": start,
                "end": end,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        user_id = d.pop("user_id")

        start = isoparse(d.pop("start"))

        end = isoparse(d.pop("end"))

        schedule_override_input_schema = cls(
            user_id=user_id,
            start=start,
            end=end,
        )

        schedule_override_input_schema.additional_properties = d
        return schedule_override_input_schema

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
