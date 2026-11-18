# Personal UI preferences

Decisions are recorded component by component. A locked preference is the default
for our own apps; revisit any necessary app-specific exception explicitly.
Preserve the [official shell/input/backend boundaries](official-ui-evaluation.md).
This record does not implement a library or change existing apps.

## Locked: home menu — exact Mesh carousel

Agreed 2026-11-18. The owner wants the home carousel **exactly as designed in Mesh**,
including its look and feel. Mesh's actual implementation is the authoritative
reference; the illustrative comparison is not a pixel/font/motion specification.

Reference: `m5stack-cardputer-zero-mesh-app`, commit
`5f21eebe83402119c5c3ad3a3aee3aef905fccd3`, principally
`src/view/screens/menu_screen.cpp`. Supporting file hashes are in the
[reference manifest](ui-preferences-evidence.json).

- Large centered icon above its label; faint previous/next icons at the edges.
- Current geometry: 40 px center icon font, 28 px neighbor icon font, 40% neighbor
  opacity, 12 px edge offsets and 10 px icon/label gap. Label uses the existing
  17 px regular standard-font path with the existing 18 px fallback.
- Directional slide and simultaneous fade over 180 ms, with a 46 px slide and
  the current ease-out slide path. Preserve correct direction through wraparound.
- Left/right selection, wrapping and Enter activation; retain the existing
  keyboard routing and selected-item state. Theme changes recolor without
  triggering selection animation; initial display does not animate in.
- Preserve the actual light/dark home appearance, including Mesh's current
  primary/disabled colors and surface treatment. A global palette decision for
  other components is still open; do not silently substitute the comparison's
  palette for this exact reference.
- Preserve the reference home geometry: 320×170, 30 px title region and content
  below it. The home implementation has no added bottom function-key lane;
  do not import the illustrative preview's footer as an approved preference.

App-specific destinations, labels and appropriate icon glyphs can represent the
new app's own functions. That is content substitution, not permission to
redesign the carousel. Preserve attribution and the selected official foundation's
lifecycle/focus ownership when later implementing reuse.

## Still to decide

- Submenu lists and selected-row appearance.
- Body/supporting typography and spacing outside the locked home reference.
- Overall palette policy and app-specific accent choices.
- Status/title bars and footer actions outside this home reference.
- Editors/forms, Help, confirmations, notifications and progress.

No implementation, extraction, new timing measurement, device test or global
restyling is claimed by this decision record.

[Principles](library-principles.md) · [Inventory](library-inventory.md)
