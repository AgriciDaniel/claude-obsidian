---
title: Claude Code Remote Control — Accès mobile
type: wiki
status: active
created: 2026-05-07
origin: Chat #2 — Lancer Chef Tool depuis téléphone
---

# Claude Code Remote Control — Accès mobile

## Source brute
Chat du 7 mai sur comment lancer et accéder à Claude Code depuis un téléphone iOS/Android, en utilisant la feature Remote Control d'Anthropic.

## Résumé utile
**Remote Control** permet de contrôler une session Claude Code du desktop depuis l'app Claude sur téléphone :
- **Installation** : Claude Code v2.1.51+ + app Claude sur téléphone + compte Claude Pro/Team/Enterprise
- **Lancer** : `claude --remote-control` sur l'ordi
- **Connecter** : Même compte sur le téléphone → session visible immédiatement
- **Notifications push** : Activables via `/config` "Push when Claude decides"
- **Auto-activation** : `/config` → "Enable Remote Control for all sessions" = `true`

## Décisions / idées clés
- **Solution officielle** : Remote Control est le chemin Anthropic (pas de workaround)
- **Zero friction** : Pas de QR codes ni manuel—session en cours se sync direct
- **Notifications** : Utile pour tâches longues (alertes quand terminées)
- **Auto-enable** : Recommandé pour workflows mobiles fréquents

## Actions
- [ ] Vérifier version Claude Code : `claude --version` (>= v2.1.51)
- [ ] Installer app Claude sur téléphone (iOS ou Android)
- [ ] Lancer `claude --remote-control` sur desktop
- [ ] Se connecter avec même compte sur téléphone
- [ ] Tester accès session en cours
- [ ] Optionnel : Activer notifications via `/config`
- [ ] Optionnel : Auto-enable Remote Control via `/config`

## Wikilinks
- [[claude-code]]
- [[mobile-workflow]]
- [[config-settings]]
