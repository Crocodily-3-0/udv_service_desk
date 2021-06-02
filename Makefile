CODE = src
TESTS = tests

ALL = $(CODE) $(TESTS)

VENV ?= venv

venv:
	sudo python3.8 -m venv $(VENV)
	$(VENV)/bin/python3.8 -m pip install --upgrade pip
	$(VENV)/bin/python3.8 -m pip install poetry
	$(VENV)/bin/poetry install

# for Windows:
win_venv:
	python -m venv $(VENV)
	$(VENV)\Scripts\python -m pip install --upgrade pip
	$(VENV)\Scripts\python -m pip install poetry
	$(VENV)\Scripts\poetry install


setup:
	$(VENV)/bin/python setup.py install


test:
	$(VENV)/bin/pytest -v tests


win_test:
	$(VENV)\Scripts\pytest -v tests


lint:
	$(VENV)/bin/flake8 --jobs 4 --statistics --show-source $(ALL)
	$(VENV)/bin/pylint --jobs 4 --rcfile=setup.cfg $(CODE)
	$(VENV)/bin/black --skip-string-normalization --check $(ALL)


win_lint:
	$(VENV)\Scripts\flake8 --jobs 4 --statistics --show-source $(ALL)
	$(VENV)\Scripts\pylint --jobs 4 --rcfile=setup.cfg $(CODE)
	$(VENV)\Scripts\black --skip-string-normalization --check $(ALL)


format:
	$(VENV)/bin/isort --apply --recursive $(ALL)
	$(VENV)/bin/black --skip-string-normalization $(ALL)
	$(VENV)/bin/autoflake --recursive --in-place --remove-all-unused-imports $(ALL)
	$(VENV)/bin/unify --in-place --recursive $(ALL)


win_format:
	$(VENV)\Scripts\isort --apply --recursive $(ALL)
	$(VENV)\Scripts\black --skip-string-normalization $(ALL)
	$(VENV)\Scripts\autoflake --recursive --in-place --remove-all-unused-imports $(ALL)
	$(VENV)\Scripts\unify --in-place --recursive $(ALL)


up:
	uvicorn $(CODE).app:app --host=0.0.0.0 --reload


ci:	lint test

win_ci: win_lint win_test

.PHONY: venv