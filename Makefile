
.PHONY: test test-unit

PYTHON ?= python3
TEST_DIR := ./tests/unit

test: test-unit

test-unit:
	$(PYTHON) -m pytest $(TEST_DIR)

