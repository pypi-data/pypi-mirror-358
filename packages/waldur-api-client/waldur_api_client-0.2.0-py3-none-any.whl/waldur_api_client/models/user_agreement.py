import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, Union
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.agreement_type_enum import AgreementTypeEnum
from ..types import UNSET, Unset

T = TypeVar("T", bound="UserAgreement")


@_attrs_define
class UserAgreement:
    """
    Attributes:
        url (str):
        uuid (UUID):
        agreement_type (AgreementTypeEnum):
        created (datetime.datetime):
        modified (datetime.datetime):
        content (Union[Unset, str]):
    """

    url: str
    uuid: UUID
    agreement_type: AgreementTypeEnum
    created: datetime.datetime
    modified: datetime.datetime
    content: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        url = self.url

        uuid = str(self.uuid)

        agreement_type = self.agreement_type.value

        created = self.created.isoformat()

        modified = self.modified.isoformat()

        content = self.content

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "url": url,
                "uuid": uuid,
                "agreement_type": agreement_type,
                "created": created,
                "modified": modified,
            }
        )
        if content is not UNSET:
            field_dict["content"] = content

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        url = d.pop("url")

        uuid = UUID(d.pop("uuid"))

        agreement_type = AgreementTypeEnum(d.pop("agreement_type"))

        created = isoparse(d.pop("created"))

        modified = isoparse(d.pop("modified"))

        content = d.pop("content", UNSET)

        user_agreement = cls(
            url=url,
            uuid=uuid,
            agreement_type=agreement_type,
            created=created,
            modified=modified,
            content=content,
        )

        user_agreement.additional_properties = d
        return user_agreement

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
