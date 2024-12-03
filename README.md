# pydantic-strict-partial

[![PyPI version](https://badge.fury.io/py/pydantic-strict-partial.svg)](https://badge.fury.io/py/pydantic-strict-partial)
[![PyPI Supported Python Versions](https://img.shields.io/pypi/pyversions/pydantic-strict-partial.svg)](https://pypi.python.org/pypi/pydantic-strict-partial/)
[![CI](https://github.com/ADR-007/pydantic-strict-partial/actions/workflows/ci.yaml/badge.svg?branch=main)](https://github.com/ADR-007/pydantic-strict-partial/actions/workflows/ci.yaml)
![badge](https://raw.githubusercontent.com/ADR-007/pydantic-strict-partial/_xml_coverage_reports/data/main/./badge.svg)

## About

Create partial models based on the original Pydantic models. 

This makes all the fields optional. 
This **doesn't** make them nullable and **doesn't** disable validation.
The only thing it does is provide default values for those fields (`None` by default), 
so you can use `model.model_dump(exclude_unset=True)` command to receive specified values only.

The most common use case is a `PATCH` request on **FastAPI** endpoints where you want to allow partial updates.

## Installation

`pydantic-strict-partial` compatible with Python 3.10+ and Pydantic 2.1+.

### Using pip
```bash
pip install pydantic-strict-partial
```

### Using poetry
```bash
poetry add pydantic-strict-partial
```

## Usage

```python
from typing import Annotated

from annotated_types import Ge
from pydantic import BaseModel

from pydantic_strict_partial import create_partial_model


class UserSchema(BaseModel):
    name: str
    nickname: str | None
    age: Annotated[int, Ge(18)]


UserPartialUpdateSchema = create_partial_model(UserSchema)

assert UserPartialUpdateSchema(age=20).model_dump(exclude_unset=True) == {
    'age': 20
}

UserPartialUpdateSchema(name=None)  # raises ValidationError
UserPartialUpdateSchema(age=17)  # raises ValidationError

```

There is also possible to specify a limited list of fields to be partial:

```python
UserPartialUpdateSchema = create_partial_model(UserSchema, 'name', 'nickname')
```

Or to make all fields partial except for the specified ones:

```python
UserPartialCreateSchema = create_partial_model(UserSchema, required_fields=['age'])
```

## Known limitations

#### MyPy: "is not valid as a type" error

You may be faced with `Variable "UserPartialUpdateSchema" is not valid as a type` error.
There is no good solution for that. But the next approach can be used as a workaround: 

```py
class UserPartialUpdateSchema(create_partial_model(UserSchema)):  # type: ignore[misc]
    pass
```

## Alternatives

[pydantic-partial](https://github.com/team23/pydantic-partial) - it makes all fields nullable and disables all validators, which is not suitable for payload validation on `PATCH` endpoints.
