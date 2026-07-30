"""One declaration of the wiki page-type vocabulary, for docs and code to share.

Before this module the `type` vocabulary was declared in four places that did not
agree: `WIKI.md`, `skills/wiki/references/frontmatter.md`, `skills/save/SKILL.md`,
and `scripts/wiki-mode.py`. Their union held twelve values and their intersection
held two, so an agent following the canonical docs could not satisfy all four and
picked one, silently. Nothing detected the result: `lint_engine` checks that
`type` is present, never that its value means anything.

Two lists, deliberately separate, because conflating them is what made the router
look broken:

``PAGE_TYPES``
    Every value allowed in a page's `type:` frontmatter.

``ROUTABLE_TYPES``
    The subset the methodology router can place, because a new page of that type
    has a natural home. `overview`, `meta` and `fold` are excluded on purpose:
    they are singular or structural pages the product creates through a dedicated
    operation, not by asking where a new note should live. `wiki/overview.md` is
    one fixed path (`transaction.py`), and a fold may only write under
    `wiki/folds/` during an `operation_type: fold` bundle. Routing them would
    invent a destination the rest of the product does not use.

That distinction already existed in behavior; it was simply never written down,
so `VALID_TYPES` read like the vocabulary while being neither list.
"""

from __future__ import annotations


# Authoritative page vocabulary. WIKI.md's table is the source this mirrors; the
# doc now points here instead of restating the values.
PAGE_TYPES: tuple[str, ...] = (
    "source",
    "entity",
    "concept",
    "question",
    "comparison",
    "session",
    "overview",
    "meta",
    "fold",
)

# Types the router can place. See the module docstring for why the remainder are
# excluded rather than missing.
ROUTABLE_TYPES: tuple[str, ...] = (
    "source",
    "entity",
    "concept",
    "question",
    "session",
)

# `research` was accepted by the router and documented nowhere. Its routing was
# already `concept`'s folder under `generic`, so it is kept as an alias rather
# than removed: dropping an accepted CLI argument would break callers for no
# behavioral gain. Aliases resolve before routing and are not part of the
# frontmatter vocabulary; the router keeps `research`'s original destinations
# rather than rewriting them through this map, so accepted calls do not move.
LEGACY_TYPE_ALIASES: dict[str, str] = {"research": "concept"}


def route_rejection_reason(content_type: str) -> str | None:
    """Explain why ``content_type`` cannot be routed, or ``None`` when it can.

    The router used to exit on an unroutable type with no message, so a caller
    could not tell a typo from a valid type that has no filing destination. Those
    are different problems with different fixes.
    """

    if content_type in ROUTABLE_TYPES or content_type in LEGACY_TYPE_ALIASES:
        return None
    if content_type in PAGE_TYPES:
        return (
            f"type {content_type!r} is a valid page type but is not routable: "
            "it is created by a dedicated operation, not filed as a new note"
        )
    return (
        f"unknown type {content_type!r}; valid page types are "
        f"{', '.join(PAGE_TYPES)}"
    )


__all__ = [
    "LEGACY_TYPE_ALIASES",
    "PAGE_TYPES",
    "ROUTABLE_TYPES",
    "route_rejection_reason",
]
