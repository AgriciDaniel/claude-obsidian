# claude-obsidian Makefile
# Test runner entry points for DragonScale and vault tooling.

.PHONY: test test-address test-tiling setup-dragonscale clean-test-state help

help:
	@echo "claude-obsidian developer targets:"
	@echo "  make test              Run all DragonScale tests"
	@echo "  make test-address     scripts/allocate-address.sh tests (shell)"
	@echo "  make test-tiling      scripts/tiling-check.py tests (python, no ollama required)"
	@echo "  make setup-dragonscale Run bin/setup-dragonscale.sh against this vault"
	@echo "  make clean-test-state Remove runtime lockfiles and tiling cache"

test: test-address test-tiling
	@echo ""
	@echo "All tests passed."

test-address:
	@echo "=== test_allocate_address.sh ==="
	@bash tests/test_allocate_address.sh

test-tiling:
	@echo "=== test_tiling_check.py ==="
	@python3 tests/test_tiling_check.py

setup-dragonscale:
	@bash bin/setup-dragonscale.sh

clean-test-state:
	@rm -f .vault-meta/.address.lock .vault-meta/.tiling.lock .vault-meta/tiling-cache.json .vault-meta/tiling-cache.*.tmp
	@echo "Runtime lockfiles and tiling cache removed."
