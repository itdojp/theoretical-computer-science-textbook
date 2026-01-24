PYTHON ?= python3
VENV_DIR ?= .venv
VENV_PY := $(VENV_DIR)/bin/python
DEPS_STAMP := $(VENV_DIR)/.deps_installed

.PHONY: test
test: $(DEPS_STAMP)
	PYTHONPATH=python $(VENV_PY) -m pytest -q python/tests

$(VENV_PY):
	$(PYTHON) -m venv $(VENV_DIR)

$(DEPS_STAMP): python/requirements-dev.txt | $(VENV_PY)
	$(VENV_PY) -m pip install -U pip
	$(VENV_PY) -m pip install -r python/requirements-dev.txt
	touch $(DEPS_STAMP)

.PHONY: clean
clean:
	rm -rf $(VENV_DIR)
