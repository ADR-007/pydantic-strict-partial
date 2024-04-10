# pydantic-strict-partial

Like [pydantic-partial](https://github.com/team23/pydantic-partial), but respects all the validators, and not nullable field.

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

## About

Create partial models from your normal pydantic models. 
Partial models will allow some or all fields to be optional and thus not be required when creating the model instance.

The most common use case is a PATCH request on FastAPI endpoints where you want to allow partial updates.

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
