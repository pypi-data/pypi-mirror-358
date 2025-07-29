import datetime
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define, field as _attrs_field
from dateutil.parser import isoparse

if TYPE_CHECKING:
    from ..models.schedule_shift_user_schema import ScheduleShiftUserSchema


T = TypeVar("T", bound="ScheduleShiftSchema")


@_attrs_define
class ScheduleShiftSchema:
    """
    Attributes:
        start (datetime.datetime):
        end (datetime.datetime):
        users (list['ScheduleShiftUserSchema']):
    """

    start: datetime.datetime
    end: datetime.datetime
    users: list["ScheduleShiftUserSchema"]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        start = self.start.isoformat()

        end = self.end.isoformat()

        users = []
        for users_item_data in self.users:
            users_item = users_item_data.to_dict()
            users.append(users_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "start": start,
                "end": end,
                "users": users,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.schedule_shift_user_schema import ScheduleShiftUserSchema

        d = src_dict.copy()
        start = isoparse(d.pop("start"))

        end = isoparse(d.pop("end"))

        users = []
        _users = d.pop("users")
        for users_item_data in _users:
            users_item = ScheduleShiftUserSchema.from_dict(users_item_data)

            users.append(users_item)

        schedule_shift_schema = cls(
            start=start,
            end=end,
            users=users,
        )

        schedule_shift_schema.additional_properties = d
        return schedule_shift_schema

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
