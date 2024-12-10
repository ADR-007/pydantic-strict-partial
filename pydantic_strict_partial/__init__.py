"""Module for creating partial Pydantic models."""

from typing import Any, TypeVar

from pydantic import BaseModel, create_model

__all__ = ["create_partial_model"]

from pydantic.fields import FieldInfo

T = TypeVar("T", bound=BaseModel)


def create_partial_model(
    model: type[T],
    *optional_fields: str,
    required_fields: list[str] | None = None,
    default_value: Any = None,  # noqa: ANN401
) -> type[T]:
    """Create a partial model from the given model class.

    :param model: The model class to create a partial model from.
    :param optional_fields: The fields to make optional.
        If None, all fields will be made optional.
    :param required_fields: The fields to make required.
        If None, no fields will be made required.
    :param default_value: The default value to use for optional fields.
    :return: The partial model class.
    """
    fields = {}
    for field in optional_fields or model.model_fields.keys():
        if required_fields and field in required_fields:
            continue

        field_info = model.model_fields[field]

        fields[field] = (
            field_info.rebuild_annotation(),
            FieldInfo.merge_field_infos(
                field_info,
                default=default_value,
                # Annotation and metadata are already populated.
                # Remove them to avoid conflicts:
                annotation=None,
                metadata=[],
            ),
        )

    return create_model(
        model.__name__ + "Partial",
        __base__=model,
        **fields,  # type: ignore[call-overload]
    )
