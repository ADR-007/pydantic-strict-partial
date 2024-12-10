from typing import Annotated

import pytest
from annotated_types import Ge
from pydantic import Base64Bytes, BaseModel, Field, ValidationError, field_validator
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


@pytest.fixture(scope="session")
def something_partial_cls() -> type[Something]:
    return create_partial_model(Something)


def test_partial_model_has_only_default_values_different_from_original(
    something_partial_cls: type[Something],
) -> None:
    for field_name in something_partial_cls.model_fields:
        original_field_info = Something.model_fields[field_name]
        partial_field_info = something_partial_cls.model_fields[field_name]

        for attribute in FieldInfo.__slots__:
            original_value = getattr(original_field_info, attribute)
            partial_value = getattr(partial_field_info, attribute)
            if attribute == "default":
                assert partial_value is None
            else:
                assert partial_value == original_value


def test_create_model_with_partial_data(something_partial_cls: type[Something]) -> None:
    something_partial = something_partial_cls(
        aliased_field="some value",
        nullable=None,
    )

    assert something_partial.model_dump(exclude_unset=True) == {
        "aliased": "some value",
        "nullable": None,
    }


def test_create_model_with_all_data(something_partial_cls: type[Something]) -> None:
    something_partial = something_partial_cls(
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


def test_not_nullable_field_does_not_accept_none(
    something_partial_cls: type[Something],
) -> None:
    with pytest.raises(ValidationError):
        something_partial_cls(aliased_field=None)  # type: ignore[arg-type]


def test_validators_from_annotation_is_executed(
    something_partial_cls: type[Something],
) -> None:
    with pytest.raises(ValidationError):
        something_partial_cls(with_validator=-1)


def test_field_validator_is_executed(something_partial_cls: type[Something]) -> None:
    with pytest.raises(ValidationError):
        something_partial_cls(with_field_info=-1)


def test_custom_validator_is_executed(something_partial_cls: type[Something]) -> None:
    with pytest.raises(ValidationError):
        something_partial_cls(custom_validated=-1)


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


def test_field_with_annotated_validator() -> None:
    """Test that field with annotated validator is correctly handled.

    Bug report:
        library doesn't work with Base64Bytes annotated fields.
        error:
            {PydanticUserError}PydanticUserError(
                "'EncodedBytes' cannot annotate 'function-after'."
            )
        pydantic versions:
            pydantic      2.10.3
            pydantic-core 2.27.1
    """

    class Model(BaseModel):
        field: Base64Bytes

    model_partial_class = create_partial_model(Model)
    instance = model_partial_class.model_validate({"field": "AAAB"})

    assert instance.field == b"\x00\x00\x01"
