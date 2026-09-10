# claude-obsidian deterministic developer entry points.

PYTHON ?= python3
export PYTHONDONTWRITEBYTECODE := 1

.PHONY: help test test-python test-shell test-contracts test-package validate \
	setup-dragonscale setup-retrieve setup-mode clean-test-state

help:
	@echo "claude-obsidian developer targets:"
	@echo "  make test             Run every hermetic Python and shell test, then contracts"
	@echo "  make test-python      Run each tests/test_*.py file in isolation"
	@echo "  make test-shell       Run each tests/test_*.sh file in isolation"
	@echo "  make test-contracts   Execute canonical product/capability verification"
	@echo "  make test-package     Validate portable skill, hook, and manifest metadata"
	@echo "  make validate         Run package and contract validators without the test suite"
	@echo "  make setup-*          Run an opt-in legacy extension setup helper"

test: test-python test-shell test-contracts test-package
	@echo "All hermetic tests and executable contracts passed."

test-python:
	@set -eu; for test_file in tests/test_*.py; do \
		echo "=== $$test_file ==="; \
		$(PYTHON) "$$test_file"; \
	done

test-shell:
	@set -eu; for test_file in tests/test_*.sh; do \
		echo "=== $$test_file ==="; \
		bash "$$test_file"; \
	done

test-contracts:
	@$(PYTHON) scripts/claude-obsidian.py contracts --check-only
	@$(PYTHON) scripts/claude-obsidian.py contracts --verify

test-package:
	@$(PYTHON) scripts/claude-obsidian.py package validate

validate: test-contracts test-package

setup-dragonscale:
	@bash scripts/setup-dragonscale.sh

setup-retrieve:
	@bash scripts/setup-retrieve.sh

setup-mode:
	@bash scripts/setup-mode.sh

clean-test-state:
	@rm -rf .vault-meta/mutation.lock .vault-meta/mutation.lock.reaping-* \
		.vault-meta/transactions .vault-meta/capture .vault-meta/capabilities \
		.vault-meta/chunks .vault-meta/bm25 .vault-meta/locks \
		.vault-meta/.address.lock.d .vault-meta/.address.lock.d.reaping-* \
		.vault-meta/.address.lock.d.reaper \
		.vault-meta/.wiki-lock.meta.d .vault-meta/.wiki-lock.meta.d.reaping-* \
		.vault-meta/.wiki-lock.meta.d.reaper
	@rm -f .vault-meta/.address.lock .vault-meta/.tiling.lock .vault-meta/.bm25.lock \
		.vault-meta/.embed-cache.lock .vault-meta/.wiki-lock.meta \
		.vault-meta/tiling-cache.json .vault-meta/tiling-cache.*.tmp \
		.vault-meta/embed-cache.json .vault-meta/embed-cache.*.tmp \
		.vault-meta/transport.json .vault-meta/transport.*.tmp \
		.vault-meta/mode.json .vault-meta/mode.*.tmp .vault-meta/hook.log
	@echo "Runtime locks, caches, and generated state removed."
