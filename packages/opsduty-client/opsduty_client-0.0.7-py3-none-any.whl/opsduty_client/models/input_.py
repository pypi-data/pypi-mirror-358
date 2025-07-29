from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define, field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="Input")


@_attrs_define
class Input:
    """
    Attributes:
        page_size (Union[None, Unset, int]):
        before (Union[None, Unset, str]):
        after (Union[None, Unset, str]):
    """

    page_size: Union[None, Unset, int] = UNSET
    before: Union[None, Unset, str] = UNSET
    after: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        page_size: Union[None, Unset, int]
        if isinstance(self.page_size, Unset):
            page_size = UNSET
        else:
            page_size = self.page_size

        before: Union[None, Unset, str]
        if isinstance(self.before, Unset):
            before = UNSET
        else:
            before = self.before

        after: Union[None, Unset, str]
        if isinstance(self.after, Unset):
            after = UNSET
        else:
            after = self.after

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if page_size is not UNSET:
            field_dict["page_size"] = page_size
        if before is not UNSET:
            field_dict["before"] = before
        if after is not UNSET:
            field_dict["after"] = after

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()

        def _parse_page_size(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        page_size = _parse_page_size(d.pop("page_size", UNSET))

        def _parse_before(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        before = _parse_before(d.pop("before", UNSET))

        def _parse_after(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        after = _parse_after(d.pop("after", UNSET))

        input_ = cls(
            page_size=page_size,
            before=before,
            after=after,
        )

        input_.additional_properties = d
        return input_

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
