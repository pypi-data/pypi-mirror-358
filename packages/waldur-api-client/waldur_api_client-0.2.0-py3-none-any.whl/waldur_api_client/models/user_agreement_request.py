from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.agreement_type_enum import AgreementTypeEnum
from ..types import UNSET, Unset

T = TypeVar("T", bound="UserAgreementRequest")


@_attrs_define
class UserAgreementRequest:
    """
    Attributes:
        agreement_type (AgreementTypeEnum):
        content (Union[Unset, str]):
    """

    agreement_type: AgreementTypeEnum
    content: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        agreement_type = self.agreement_type.value

        content = self.content

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "agreement_type": agreement_type,
            }
        )
        if content is not UNSET:
            field_dict["content"] = content

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        agreement_type = AgreementTypeEnum(d.pop("agreement_type"))

        content = d.pop("content", UNSET)

        user_agreement_request = cls(
            agreement_type=agreement_type,
            content=content,
        )

        user_agreement_request.additional_properties = d
        return user_agreement_request

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
