.PHONY: clean clean-pyc test upload

all: clean clean-pyc test

clean: clean-pyc
	rm -rf build
	rm -rf dist
	rm -rf *.egg-info
	rm -rf tests/res/t
	find . -name '.DS_Store' -exec rm -f {} \;

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} \;
	find . -name '*.pyo' -exec rm -f {} \;
	find . -name '*~' -exec rm -f {} \;
	rm -rf tests/source
	rm -rf tests/build

test:
	~/.virtualenvs/clay/bin/py.test --cov-config .coveragerc --cov clay tests/
	rm -rf tests/__pycache__

upload: clean
	python setup.py sdist upload

