SRC = $(wildcard ./*.ipynb)

all: build docs clean

build: $(SRC)
	nbdev_build_lib

docs: $(SRC)
	nbdev_build_docs
	touch docs

test:
	nbdev_test_nbs

pypi: dist
	twine upload --repository pypi dist/*

dist: clean
	python setup.py sdist bdist_wheel

clean:
	nbdev_clean_nbs
	rm -rf dist
