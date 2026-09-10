# DragonScale compatibility extension

DragonScale is an optional set of memory-maintenance experiments. The base
vault does not require it. The extension consists of four independent ideas;
their maturity and dependencies differ.

## Provisioning

Preview the create-only setup transaction:

```bash
bash scripts/setup-dragonscale.sh --vault <vault>
```

Apply only after reviewing the missing paths:

```bash
bash scripts/setup-dragonscale.sh --vault <vault> \
  --generated-at <ISO-UTC> --approved-plan-sha256 <reviewed-sha256> --apply
```

Setup creates only missing address-counter, tiling-threshold, legacy-exception,
and legacy-manifest files. It never replaces existing values, downloads a
model, changes product scripts, probes a service, or modifies notes.

## 1. Extractive log folds

`wiki-fold` creates a bounded rollup from recent `wiki/log.md` entries. A fold
must be:

- extractive—every statement points to a child entry;
- additive—children remain unchanged;
- structurally idempotent—the same input set produces the same fold identity;
- previewed before one transaction applies the fold, index, and log update.

Folds are navigation aids, not new evidence. Delete or revert only the fold
operation if a rollup is unhelpful.

## 2. Stable addresses

Modern operations request addresses through the main transaction bundle. The
engine allocates the counter, injects page frontmatter, and updates the legacy
address map inside the same journal. Do not call the legacy allocator for new
ingestion workflows.

`scripts/allocate-address.sh` remains a read-only compatibility diagnostic for
older vaults. It accepts an explicit vault and never creates or acquires a lock.
Its output does not replace the transaction engine's expected-hash, allocation,
concurrency, or rollback guarantees.

## 3. Semantic tiling diagnostics

`scripts/tiling-check.py` embeds eligible pages through an Ollama model and
compares every distinct page pair for possible duplication. It is optional and
its seed thresholds are uncalibrated. A score is a review signal, not proof
that two pages should be merged.

Preview without writing a report:

```bash
python3 scripts/tiling-check.py --vault <vault> --peek
```

Remote Ollama hosts are refused unless `--allow-remote-ollama` is supplied.
Calibrate thresholds on labeled examples from the selected vault before using
them as policy. If Ollama or the model is absent, report that capability state;
do not imply the check ran.

## 4. Boundary scoring

`scripts/boundary-score.py` ranks pages that may deserve more research using
current graph structure and recency. It is deterministic and read-only:

```bash
python3 scripts/boundary-score.py --vault <vault> --json --top 10
```

The score proposes attention; it does not establish importance or truth. Use a
candidate as an autoresearch topic only after reviewing its underlying links
and the research budget.

## Failure and recovery

- A setup conflict means an expected path changed; generate a new plan.
- An interrupted setup uses the normal transaction recovery command.
- A corrupt legacy counter should be rebuilt from observed addresses only after
  checking duplicates and the address map.
- A tiling cache or BM25 index is derived and may be regenerated. Source pages
  and provenance ledgers are not derived caches.
- Disabling DragonScale requires no bulk rewrite. Stop invoking the optional
  helpers; existing fold pages and addresses remain normal vault content.

## Verification

Run the relevant hermetic tests or the full suite:

```bash
make test
```

Capability maturity is based on executed checks, not the presence of a setup
file. Keep each mechanism optional and fail closed when its prerequisites are
unavailable.
