
VENV_PATH = .venv

PYTHON = $(shell [ -x $(VENV_PATH)/bin/python ] && echo "$(VENV_PATH)/bin/python" || echo "python")

install-requirements:
	$(PYTHON) -m pip install -r requirements.txt -r requirements-dev.txt

black:
	$(PYTHON) -m black -l 120 -S ./app ./tests

isort:
	$(PYTHON) -m isort -l 120 --profile black ./app ./tests

autoflake:
	$(PYTHON) -m autoflake --in-place --remove-all-unused-imports --remove-unused-variables --expand-star-imports --recursive ./app ./tests

check-black:
	$(PYTHON) -m black --check --diff -l 120 -S ./app ./tests

check-isort:
	$(PYTHON) -m isort -l 120 --profile black ./app ./tests -c

check-flake8:
	$(PYTHON) -m flake8 --ignore=W503,E711,E712,W291,E704 --max-line-length=120 ./app ./tests

pytest:
	$(PYTHON) -m pytest ./tests

lint: autoflake isort black

check: check-black check-isort check-flake8
