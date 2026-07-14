.PHONY: install
install:
	uv sync --all-groups

.PHONY: test
test:
	uv run pytest -x src/clay tests

.PHONY: lint
lint:
	uv run ruff check src/clay tests
	uv run ty check src/clay

.PHONY: lintfix
lintfix:
	uv run ruff check src/clay tests --fix

.PHONY: coverage
coverage:
	uv run pytest --cov-config=pyproject.toml --cov-report html --cov src/clay tests
