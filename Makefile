lint:
	uv run --group dev ruff check pydantic_strict_partial tests.py
	uv run --group dev ruff format --check pydantic_strict_partial tests.py
	uv run --group dev mypy pydantic_strict_partial tests.py

lint-fix:
	uv run --group dev ruff format pydantic_strict_partial tests.py
	uv run --group dev ruff check --fix pydantic_strict_partial tests.py
