from typing import Annotated

import pytest
from annotated_types import Ge
from pydantic import BaseModel, Field, ValidationError, field_validator
from pydantic.fields import FieldInfo

from pydantic_strict_partial import create_partial_model


class Something(BaseModel):
    aliased: str = Field(alias="aliased_field")
    with_default: int = 42
    with_validator: Annotated[int, Ge(0)]
    with_field_info: int = Field(..., ge=0, description="Field description")
    nullable: str | None
    nullable_with_default: str | None = None
    union_field: str | int
    custom_validated: int

    @field_validator("custom_validated")
    @classmethod
    def validate_custom_validated(cls, value: int) -> int:
        if value < 0:
            raise ValueError("Value must be greater than 4")

        return value


SomethingPartial = create_partial_model(Something)


def test_partial_model_has_only_default_values_different_from_original() -> None:
    for field_name in Something.model_fields:
        original_field_info = Something.model_fields[field_name]
        partial_field_info = SomethingPartial.model_fields[field_name]

        for attribute in FieldInfo.__slots__:
            original_value = getattr(original_field_info, attribute)
            partial_value = getattr(partial_field_info, attribute)
            if attribute == "default":
                assert partial_value is None
            else:
                assert partial_value == original_value


def test_create_model_with_partial_data() -> None:
    something_partial = SomethingPartial(
        aliased_field="some value",
        nullable=None,
    )

    assert something_partial.model_dump(exclude_unset=True) == {
        "aliased": "some value",
        "nullable": None,
    }


def test_create_model_with_all_data() -> None:
    something_partial = SomethingPartial(
        aliased_field="some value",
        with_default=42,
        with_validator=5,
        with_field_info=42,
        nullable=None,
        nullable_with_default=None,
        union_field="some value",
        custom_validated=5,
    )

    assert something_partial.model_dump(exclude_unset=True) == {
        "aliased": "some value",
        "with_default": 42,
        "with_validator": 5,
        "with_field_info": 42,
        "nullable": None,
        "nullable_with_default": None,
        "union_field": "some value",
        "custom_validated": 5,
    }


def test_not_nullable_field_does_not_accept_none() -> None:
    with pytest.raises(ValidationError):
        SomethingPartial(aliased_field=None)  # type: ignore[arg-type]


def test_validators_from_annotation_is_executed() -> None:
    with pytest.raises(ValidationError):
        SomethingPartial(with_validator=-1)


def test_field_validator_is_executed() -> None:
    with pytest.raises(ValidationError):
        SomethingPartial(with_field_info=-1)


def test_custom_validator_is_executed() -> None:
    with pytest.raises(ValidationError):
        SomethingPartial(custom_validated=-1)


def test_make_some_fields_optional() -> None:
    class Model(BaseModel):
        required: str
        required2: str

    model_partial_class = create_partial_model(
        Model,
        "required",
    )

    model_partial_class(required2="value")

    with pytest.raises(ValidationError):
        model_partial_class(required="value")


def test_make_some_fields_required() -> None:
    class Model(BaseModel):
        required: str
        required2: str

    model_partial_class = create_partial_model(
        Model,
        required_fields=["required"],
    )

    model_partial_class(required="value")

    with pytest.raises(ValidationError):
        model_partial_class(required2="value")
