"""Deterministic fake editor.

The editor applies bounded, scripted improvements to a descriptor: each
directive improves its quality dimension by one fixed step, capped. It
never changes the dish, the objects, the item count, the plating style,
or the merchant's brand tokens -- those are exactly the things an edit
must not fabricate, and the QA and publish gates verify it. Editing
cannot fix a count mismatch or an unverifiable count; those photos are
withheld by QA instead of being "fixed" by invention.
"""

from __future__ import annotations

from dataclasses import replace

from .descriptors import ImageDescriptor

EDIT_STEP = 0.2
EDIT_CAP = 0.95

DIRECTIVE_FIELDS = {
    "improve_sharpness": "sharpness",
    "recenter_composition": "composition",
    "restore_natural_color": "color",
    "improve_plating": "plating",
    # "verify_count" deliberately maps to nothing: counts are never edited.
}


def edit(descriptor: ImageDescriptor, directives) -> ImageDescriptor:
    """Apply one bounded edit step per targeted dimension."""
    changes = {}
    for directive in directives:
        field = DIRECTIVE_FIELDS.get(directive)
        if field is None:
            continue
        changes[field] = round(min(EDIT_CAP, getattr(descriptor, field) + EDIT_STEP), 10)
    return replace(descriptor, **changes)
