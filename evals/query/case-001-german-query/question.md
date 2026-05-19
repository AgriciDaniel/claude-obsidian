# Query case-001-german-query

Run the query twice against the same vault. Both should hit `[[IHK]]`.

## Variant A (German)

> Was muss ich bei der IHK-Anmeldung als Solo-Gründer wissen?

## Variant B (English)

> How does the German chamber of commerce work for solo founders?

The skill must return an answer grounded in `[[IHK]]` in both cases.
A failure mode would be: variant B fails to find the page because the
title is German. Dual-form retrieval via `aliases:` prevents this.
