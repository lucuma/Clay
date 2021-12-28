.PHONY: test
test:
	pytest -x clay tests

.PHONY: lint
lint:
	flake8 --config=setup.cfg clay tests

.PHONY: coverage
coverage:
	pytest --cov-config=.coveragerc --cov-report html --cov clay clay tests

.PHONY: install
install:
	pip install -e .[test,dev]
	# pip install -r docs/requirements.txt
	# pre-commit install
