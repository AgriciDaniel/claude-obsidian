# claude-obsidian Makefile
# Test runner entry points for DragonScale and vault tooling.

.PHONY: test test-address test-tiling test-boundary test-bm25 test-retrieve \
        test-lock test-concurrent test-mode test-contextual setup-dragonscale \
        setup-retrieve setup-mode clean-test-state help \
        test-net test-render test-browser check-rules render-rules setup-live \
        test-introspect check-core scan verify-core

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
	@echo "  make test-net         scripts/net-policy.py tests (python, hermetic)"
	@echo "  make test-render      scripts/render-rules.py tests (python, hermetic)"
	@echo "  make test-browser     scripts/detect-browser.sh tests (shell, hermetic)"
	@echo "  make test-introspect  scripts/core-introspect.py tests (python, hermetic)"
	@echo "  make check-rules      Drift gate: rendered rule files match rules/"
	@echo "  make check-core       Drift gate: capabilities.json matches the source tree"
	@echo "  make scan             Rebuild .vault-meta/capabilities.json from source"
	@echo "  make verify-core      EXECUTE every endpoint; red if any is broken"
	@echo "  make setup-live       Set up v2.0 Live Core (net, browser, rules, workflows)"
	@echo "  make setup-dragonscale Run bin/setup-dragonscale.sh against this vault"
	@echo "  make setup-retrieve   Run bin/setup-retrieve.sh against this vault (opt-in v1.7)"
	@echo "  make setup-mode       Run bin/setup-mode.sh to pick a methodology mode (opt-in v1.8)"
	@echo "  make clean-test-state Remove runtime lockfiles and tiling/embed caches"

test: test-address test-tiling test-boundary test-bm25 test-retrieve test-lock test-concurrent test-mode test-contextual \
      test-net test-render test-browser test-introspect check-rules check-core
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

test-net:
	@echo "=== test_net_policy.py ==="
	@python3 tests/test_net_policy.py

test-render:
	@echo "=== test_render_rules.py ==="
	@python3 tests/test_render_rules.py

test-browser:
	@echo "=== test_detect_browser.sh ==="
	@bash tests/test_detect_browser.sh

test-introspect:
	@echo "=== test_core_introspect.py ==="
	@python3 tests/test_core_introspect.py

# Drift gate. rules/ is the single source of truth; the six rendered agent
# dialects are build artifacts. If someone hand-edits a rendered file, this
# goes red. That is what keeps single-sourcing from quietly becoming six copies.
check-rules:
	@echo "=== render-rules check ==="
	@python3 scripts/render-rules.py check

render-rules:
	@python3 scripts/render-rules.py render

# Drift gate for the plugin's self-knowledge. capabilities.json is derived from
# source, so it goes stale the moment a skill, script, or workflow is added and
# nobody rescans. A stale manifest is worse than none: the plugin would confidently
# report a surface it no longer has.
check-core:
	@echo "=== core-introspect check ==="
	@python3 scripts/core-introspect.py check

# Rebuild the manifest after adding or removing an endpoint.
scan:
	@python3 scripts/core-introspect.py scan

# EXECUTES every entry point the manifest claims exists. This is the one that
# proves the surface is real rather than merely declared; `check` only proves the
# JSON matches the source. Not in `make test`: it shells out ~90 times.
verify-core:
	@python3 scripts/core-introspect.py verify

setup-live:
	@bash bin/setup-live.sh

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
