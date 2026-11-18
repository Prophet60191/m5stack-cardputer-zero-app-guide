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

## Locked: submenu-list selection and navigation cues

Confirmed 2026-11-18: use Mesh's rounded selected row, subtle background fill
and colored stripe on the left. Reference: the same Mesh commit above,
`src/view/widgets/list_selection.h`, `style_list_row()` / `select_list_row()`.
The existing implementation uses a 6 px radius, palette button fill and 3 px
left border in the primary color; changing selection clears the old row's
selection styling and scrolls the newly selected row into view. Screens retain
their own item identity and navigation state.

Additional rules supplied by the owner on 2026-11-18:

- If the highlighted entry opens a submenu, show a right-facing chevron (`>`)
  at the right of the row. The indicators for other row types are still undecided.
- If content extends beyond the visible screen, show a slim bar on the right
  with a moving position marker, so the user can see that more content exists.
  Keep it available as navigation reveals items above/below; omit it when all
  content fits. Reserve space so it does not obscure labels or chevrons.
- Use wrap-around list navigation: Down from the last selectable entry moves
  to the first; Up from the first moves to the last. Scroll the visible list
  to keep the new selection in view, including after wrapping. Moving selection
  does not activate/open the entry.
- The position bar is conditional on actual content exceeding the visible list
  area, not merely on the list being nonempty. Wrapping updates its marker to
  the new position. An empty list has no selection; a single selectable item
  remains selected. Preserve this behavior if item count or row height changes.
- Visual reference for that bar: NFC Tools' Settings main page, inspected in
  `build/amber/settings.png` and `src/ui/app.cpp::App::list`. The example shows
  three of five rows, a thin right-side track and an accent-colored marker.

The NFC source/render reference is recorded by hash in the manifest and comes
from an uncommitted working tree, not its HEAD alone. Its current list renderer
draws the bar for every nonempty list and draws chevrons on all displayed rows.
Those existing conditions are not the owner's specified rules; reuse the visual
reference while implementing the conditional behaviors above in any later work.
No NFC change is made here. Typography and row content are not locked by these cues.

The owner's wrap-around request is recorded as component behavior during this
preference walkthrough. No reusable list implementation exists from this record,
and this update does not claim it has been applied to an existing app.

## Still to decide

- Affordances for list entries that do not open submenus.
- Body/supporting typography and spacing outside the locked home reference.
- Overall palette policy and app-specific accent choices.
- Status/title bars and footer actions outside this home reference.
- Editors/forms, Help, confirmations, notifications and progress.

No implementation, extraction, new timing measurement, device test or global
restyling is claimed by this decision record.

[Principles](library-principles.md) · [Inventory](library-inventory.md)
