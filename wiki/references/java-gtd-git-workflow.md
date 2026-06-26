---
type: reference
title: java-gtd — Git workflow
status: active
created: 2026-06-24
updated: 2026-06-24
tags:
  - git
  - java-gtd
  - workflow
related:
  - "[[java-gtd]]"
---

# Git workflow — java-gtd

## Regla principal

**Nunca hacer push directo a `master`.** El usuario es el único que mergea a master, desde GitHub.

## Flujo correcto

```bash
# 1. Asegurarse de estar en master actualizado
git checkout master
git pull

# 2. Crear rama
git checkout -b feature/<nombre>   # o fix/, chore/, etc.

# 3. Trabajar, commitear
git add <archivos>
git commit -m "feat(...): ..."

# 4. Pushear SOLO la rama
git push -u origin feature/<nombre>

# 5. El usuario abre el PR desde GitHub y mergea
# 6. Cuando avisa que mergeó:
git checkout master
git pull
git branch -d feature/<nombre>
```

## Nunca

- `git push origin master`
- `git merge` directo a master desde Claude
- Merge automático vía `gh pr merge`
