lint:
	ruff check pydantic_strict_partial tests.py
	ruff format --check pydantic_strict_partial tests.py
	mypy pydantic_strict_partial tests.py

lint-fix:
	ruff format pydantic_strict_partial tests.py
	ruff check --fix pydantic_strict_partial tests.py