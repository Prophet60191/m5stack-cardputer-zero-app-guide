# Personal UI preferences

Decisions are recorded component by component. A locked preference is the default
for my own apps; revisit any necessary app-specific exception explicitly.
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
  below it. The position indicator in the next section is the agreed addition. The home implementation has no added bottom function-key lane;
  do not import the illustrative preview's footer as an approved preference.

App-specific destinations, labels and appropriate icon glyphs can represent the
new app's own functions. That is content substitution, not permission to
redesign the carousel. Preserve attribution and the selected official foundation's
lifecycle/focus ownership when later implementing reuse.

## Locked: home-carousel position indicator

Agreed 2026-11-26. Keep the Mesh home carousel geometry and directional
animation, and add the NFC Tools position bar below the home label. Center
the row, use NFC Tools’ vertical spacing (menu title top y=82, dot row y=138 on 320×170), and use a wider accent pill for the current slot and small muted dots
for the others, and update it with the carousel selection, including wrap.
Do not animate or add a footer for the indicator. This is distinct from the
right-edge overflow bar used on a submenu list. The [reusable LVGL component](../examples/ui-patterns/carousel-position/README.md)
and its source notes live with the guide. The same reference uses a 40 px center icon at y=33 and 28 px side icons in lanes starting at x=14 and x=270, y=69. The center icon and title share a 216 px lane at x=52.

Keep the top-bar battery percentage plain text and right-aligned when available.
No battery glyph and no fabricated percentage if the device does not report one.

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
  at the right of the row. Do not use it as a generic decoration on every row.
- If content extends beyond the visible screen, show a slim bar on the right
  with a moving position marker, so the user can see that more content exists.
  Keep it available as navigation reveals items above/below; omit it when all
  content fits. Reserve space so it does not obscure labels or chevrons.
- Use Up and Down for vertical selection (Fn+F/Fn+X on Cardputer Zero; bare F/X may be contextual aliases outside editors). Left and Right move the home carousel or adjust a focused value, never select a vertical row.
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

## Locked: On/Off setting rows

Agreed 2026-11-18: display the setting's **On** or **Off** value as text on the
right, with its name on the left. Use this instead of a drawn toggle switch or
checkmark for ordinary boolean settings. A row that changes a value inline does
not receive a submenu chevron; reserve `>` for submenu navigation.

Example: `Save history` on the left and `On` on the right. The value must reflect
the setting's known state; handling pending/unknown states and any necessary
confirmation remains part of the app's behavior contract, not a reason to display
a false On/Off value. This preference selects presentation, not new toggle or
confirmation behavior.

## Locked: direct choices and task forms

Agreed 2026-11-22: a setting with two choices changes directly on its row;
Appearance alternates Light/Dark without a submenu. More than two choices open
an appropriate selection menu with the current value selected. Inline actions
do not receive a submenu chevron. Preserve any specific consent required for
privacy, transmission or irreversible effects; do not show an unconfirmed value
as already applied.

Group everything needed for a task in one place. A channel setup form includes
its related channel, radio, sharing and save fields rather than requiring trips
through Settings. Use visible groups inside the same form, identify changes
that affect the whole radio, preserve edits on errors, and keep Save reachable
while scrolling. The form itself is the review; do not add a generic second
review page. Specific consequential changes can require targeted acknowledgment.

Use readable contrast for important values and results in both themes, plain
language for outcomes, non-color cues where color carries meaning, and
Cancel-first confirmation for irreversible deletion when Undo is unavailable.
These are my interaction preferences; they do not create a replacement shell
or a universal requirement for every project. Source and physical qualification
remain app-specific. Mesh's 0.1.15 candidate implements a focused refinement;
its verification record owns the actual results and remaining checks.

## Locked: header battery presentation

Agreed 2026-11-23: omit the battery icon from the app header. Mesh retains the
numeric charge percentage when battery data is available, with no substitute
charging/battery glyph. This is my presentation preference, not a platform
requirement or a replacement for the official shell/status source. Preserve
truthful unknown/absent state and existing backend ownership. Do not add polling
or change telemetry merely to remove a decorative icon. Other apps are not
silently migrated by this documentation update.

## Still to decide

- Presentation of immediate-action rows beyond the recorded choice rules.
- Body/supporting typography and spacing outside the locked home reference.
- Overall palette policy and app-specific accent choices.
- Status/title bars and footer actions outside this home reference.
- Editors/forms, Help, confirmations, notifications and progress.

No implementation, extraction, new timing measurement, device test or global
restyling is claimed by this decision record.

[Principles](library-principles.md) · [Inventory](library-inventory.md)
