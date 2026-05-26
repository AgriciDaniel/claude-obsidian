# claude-obsidian Makefile
# Test runner entry points for DragonScale and vault tooling.

.PHONY: test test-address test-tiling test-boundary test-bm25 test-retrieve \
        test-lock test-concurrent test-mode test-contextual setup-dragonscale \
        setup-retrieve setup-mode clean-test-state help

help:
	@echo "claude-obsidian developer targets:"
	@echo "  make test              Run all v1.7 tests (DragonScale + retrieval + concurrency)"
	@echo "  make test-address     scripts/allocate-address.sh tests (shell)"
	@echo "  make test-tiling      scripts/tiling-check.py tests (python, no ollama required)"
	@echo "  make test-boundary    scripts/boundary-score.py tests (python, no prereqs)"
	@echo "  make test-bm25        scripts/bm25-index.py tests (python, hermetic)"
	@echo "  make test-retrieve    scripts/retrieve.py + rerank.py tests (python, hermetic)"
	@echo "  make test-lock        scripts/wiki-lock.sh tests (shell, hermetic)"
	@echo "  make test-concurrent  multi-writer correctness gate (shell, hermetic)"
	@echo "  make test-mode        scripts/wiki-mode.py tests (python, hermetic)"
	@echo "  make test-contextual  scripts/contextual-prefix.py cache-floor tests (python, hermetic)"
	@echo "  make setup-dragonscale Run bin/setup-dragonscale.sh against this vault"
	@echo "  make setup-retrieve   Run bin/setup-retrieve.sh against this vault (opt-in v1.7)"
	@echo "  make setup-mode       Run bin/setup-mode.sh to pick a methodology mode (opt-in v1.8)"
	@echo "  make clean-test-state Remove runtime lockfiles and tiling/embed caches"

test: test-address test-tiling test-boundary test-bm25 test-retrieve test-lock test-concurrent test-mode test-contextual
	@echo ""
	@echo "All tests passed."

test-address:
	@echo "=== test_allocate_address.sh ==="
	@bash tests/test_allocate_address.sh

test-tiling:
	@echo "=== test_tiling_check.py ==="
	@python3 tests/test_tiling_check.py

test-boundary:
	@echo "=== test_boundary_score.py ==="
	@python3 tests/test_boundary_score.py

test-bm25:
	@echo "=== test_bm25_index.py ==="
	@python3 tests/test_bm25_index.py

test-retrieve:
	@echo "=== test_retrieve.py ==="
	@python3 tests/test_retrieve.py

test-lock:
	@echo "=== test_wiki_lock.sh ==="
	@bash tests/test_wiki_lock.sh

test-concurrent:
	@echo "=== test_concurrent_write.sh ==="
	@bash tests/test_concurrent_write.sh

test-mode:
	@echo "=== test_wiki_mode.py ==="
	@python3 tests/test_wiki_mode.py

test-contextual:
	@echo "=== test_contextual_prefix.py ==="
	@python3 tests/test_contextual_prefix.py

setup-dragonscale:
	@bash bin/setup-dragonscale.sh

setup-retrieve:
	@bash bin/setup-retrieve.sh

setup-mode:
	@bash bin/setup-mode.sh

clean-test-state:
	@rm -f .vault-meta/.address.lock .vault-meta/.tiling.lock .vault-meta/.bm25.lock \
	      .vault-meta/.embed-cache.lock .vault-meta/.wiki-lock.meta \
	      .vault-meta/tiling-cache.json \
	      .vault-meta/tiling-cache.*.tmp .vault-meta/embed-cache.json \
	      .vault-meta/embed-cache.*.tmp .vault-meta/transport.json \
	      .vault-meta/transport.*.tmp
	@rm -rf .vault-meta/chunks/ .vault-meta/bm25/ .vault-meta/locks/
	@rm -f .vault-meta/mode.json .vault-meta/mode.*.tmp .vault-meta/hook.log
	@echo "Runtime lockfiles, caches, and v1.7/v1.8 runtime artifacts removed."
