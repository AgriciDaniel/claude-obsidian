---
title: Intégration Claude Code — Guide complet
type: wiki
status: active
created: 2026-05-06
origin: Chat #1 — Chef Tool
---

# Intégration Claude Code — Guide complet

## Source brute
Chat du 6 mai portant sur l'intégration d'une session Claude Code (CHEF TOOL) dans un projet existant. Discussion autour de la récupération, l'exportation et l'archivage de sessions locales vers un CLAUDE.md project.

## Résumé utile
Comment intégrer une session Claude Code existante dans un projet :
- **Récupérer session** : `claude --resume CHEF-TOOL` ou `/stats` pour voir toutes ses sessions
- **Exporter résumé** : `/summary` dans la session active
- **Automatiser setup** : Script bash `integrate-claude-session.sh` (30 secondes)
- **Persister contexte** : Créer CLAUDE.md avec `.chef-tool-context/` subdirs
- **Synchroniser** : Script `sync-session.sh` pour mises à jour régulières

## Décisions / idées clés
- **Structure proposée** : `.chef-tool-context/` pour archiver contexte + config
- **Automatisation CLI** : Script ready-to-run pour setup complet
- **Contexte persistant** : CLAUDE.md permet chargement auto dans futures sessions
- **3 phases** : Récupération (5min) → Intégration (5min) → Version Control (2min)
- **Traceabilité** : Manifest + docs = équipe synchronisée via git

## Actions
- [ ] Télécharger 7 fichiers livrés (integrate-claude-session.sh + guides)
- [ ] Lire RECUPERER-SESSION.md en premier
- [ ] Exécuter `claude --resume CHEF-TOOL -p "/summary"` sur machine locale
- [ ] Lancer `bash integrate-claude-session.sh . CHEF-TOOL` dans project racine
- [ ] Remplir `.chef-tool-context/claude-code-session-*.md` avec contenu
- [ ] Valider avec checklist EXECUTION-CHECKLIST.md
- [ ] Commit dans git : `feat: integrate Claude Code session CHEF-TOOL`

## Wikilinks
- [[claude-code]]
- [[project-structure]]
- [[CLAUDE.md-configuration]]
- [[git-workflow]]
