"""Module for creating partial Pydantic models."""

from typing import Any, Iterable, TypeVar

from pydantic import BaseModel, create_model
from pydantic.fields import FieldInfo

__all__ = ["create_partial_model"]

T = TypeVar("T", bound=BaseModel)


def create_partial_model(
    model: type[T],
    optional_fields: Iterable[str] | None = (),
    default_value: Any = None,  # noqa: ANN401
) -> type[T]:
    """Create a partial model from the given model class.

    :param model: The model class to create a partial model from.
    :param optional_fields: The fields to make optional.
        If None, all fields will be made optional.
    :param default_value: The default value to use for optional fields.
    :return: The partial model class.
    """
    fields = {}
    for field in optional_fields or model.model_fields.keys():
        field_info = model.model_fields[field]

        fields[field] = (
            field_info.rebuild_annotation(),
            FieldInfo.merge_field_infos(field_info, default=default_value),
        )

    return create_model(
        model.__name__ + "Partial",
        __base__=model,
        **fields,  # type: ignore[call-overload]
    )
