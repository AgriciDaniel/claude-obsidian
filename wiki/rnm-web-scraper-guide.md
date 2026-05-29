---
title: RNM Web Scraper — Récupérer liste produits France AgriMer
type: wiki
status: active
created: 2026-05-07
origin: Chat #4 — Scrape RNM franceagrimer.fr
---

# RNM Web Scraper — Récupérer liste produits France AgriMer

## Source brute
Chat du 7 mai sur la récupération complète des produits du site RNM (https://rnm.franceagrimer.fr) avec sa structure hiérarchique (secteurs → groupes → sous-groupes → produits → variétés) en format Markdown.

Site : JavaScript SPA (Single Page App) — rendu dynamique, pas d'HTML statique.

## Résumé utile
**Structure RNM (5 niveaux)**
```
Secteur (5 totaux)
├─ Groupe
│  └─ Sous-groupe
│     └─ Produit/Libellé
│        └─ Variétés (exclure Catégories/Qualités)
```

**Secteurs** : Fruits et Légumes, Fleurs & plantes ornementales, Pêche et aquaculture, Beurre Œuf Fromage, Viande

**Approche extraction** :
- **Playwright + Chromium** : Méthode A (complète, 15-30 min d'exec)
- **Google Search** : Méthode B (partielle, ~60% de couverture, 0 setup)
- Sortie : `produits_rnm.md` (hiérarchie respectée) + `produits_rnm.json` (sauvegarde brute)

**Script key features**
- Hiérarchie respectée jusqu'à 5 niveaux (configurable `MAX_PROFONDEUR`)
- Filtres auto : Cat I/II/Qualité/Extra exclas via regex
- Sauvegarde incrémentale JSON (résilience crash)
- Délai 0,6s entre requêtes (politesse)
- Error handling + logging verbeux

## Décisions / idées clés
- **Production locale recommandée** : Firewall/proxy Anthropic bloque rnm.franceagrimer.fr
- **Script ready-to-run** : `scrape_rnm.py` dans repo (Playwright v1.40+)
- **Sauvegarde double** : .md (lisible) + .json (continuation si crash)
- **Heuristique variétés** : Cherche `<th>/<h2>` "Variét..." puis cellule/bloc voisin—variable par secteur

## Actions
- [ ] Télécharger `scrape_rnm.py`, `requirements.txt`, `README.md`
- [ ] Sur machine locale (hors proxy) :
  ```bash
  python3 -m venv .venv && source .venv/bin/activate
  pip install -r requirements.txt
  playwright install chromium
  python scrape_rnm.py
  ```
- [ ] Attendre 15-30 min (dépend de ~500 produits)
- [ ] Récupérer `produits_rnm.md` (sortie finale)
- [ ] Si crash → relancer (reprend depuis checkpoint JSON)
- [ ] Vérifier variétés par secteur (heuristique peut varier)

## Wikilinks
- [[data-collection]]
- [[web-scraping]]
- [[rnm-products]]
- [[market-data]]
