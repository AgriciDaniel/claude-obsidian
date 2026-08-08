---
description: Regenerate wiki/hot.md from ground truth (git + plugin version). Preserves Active Threads.
---

Read the `hot-sync` skill. Then run:

```bash
bash scripts/hot-sync.sh
```

If the vault root is not the current directory, pass it as the first argument.

After the script finishes, optionally update the Active Threads block between the HTML markers with a few short bullets. Do not rewrite Ground Truth by hand.

Usage:
- `/hot-sync` — regenerate hot cache
- `/hot` — same (alias intent; run hot-sync)
