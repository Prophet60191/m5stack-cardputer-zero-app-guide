# Personal UI preferences

Decisions are recorded component by component. A locked preference is the default
for my own apps; revisit any necessary app-specific exception explicitly.
Preserve the [official shell/input/backend boundaries](official-ui-evaluation.md).
The [App Shell](app-shell.md) is the reusable reference for the patterns below.
An app only conforms to the patterns it has actually adopted and tested.

## Locked: NFC Tools home menu for my apps

This 2026-11-26 decision replaces the earlier Mesh-only home layout. I like
the NFC Tools carousel, so that is what I use and demonstrate. It is a
personal preference, not a platform rule. For submenu selection, use the
Start form standard below.

Use the NFC Tools header, center icon and title/subtitle, shaded side icons,
position dots, divider and key hints as one composition. The standard adds a
plain right-aligned battery percentage when the device reports one. Keep
apps' own menu choices, icons and accent colors. The complete
[home-menu spec and reusable component](../examples/ui-patterns/carousel-position/README.md)
list the positions, font sizes, and ownership boundaries.

## Locked: submenu-list selection and navigation cues

The **App Shell Start form** is the current reference: a neutral fill, 6 px
rounded corners and a 3 px full-height accent stripe at the left edge. Only
the selected row has those marks. Keep the same treatment for explanation,
value, form and confirmation rows; their content layouts can differ. The
earlier Mesh implementation was the starting point for this decision.

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

The earlier NFC Tools render served as the visual reference for the position
bar. The shell’s implementation controls when it appears. This is a reusable
pattern; do not infer conformance from an older app screenshot.

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
- Additional patterns beyond the shell's basic fixed pages, form editor,
  and single-action detail footer, only when a real app needs them.
- App-specific Help, irreversible confirmations, notifications and progress.

No implementation, extraction, new timing measurement, device test or global
restyling is claimed by this decision record.

[Principles](library-principles.md) · [Inventory](library-inventory.md)
