.PHONY: clean clean-pyc test upload

all: clean clean-pyc test

clean:
	rm -rf build
	rm -rf dist
	rm -rf *.egg-info

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +

test:
	python runtests.py
	rm -rf tests/__pycache__

upload:
	clean
	clean-pyc
	python setup.py sdist upload
