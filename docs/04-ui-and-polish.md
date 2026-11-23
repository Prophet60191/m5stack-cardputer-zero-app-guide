# 4. UI and polish

Make every screen predictable, readable and usable from the keyboard. Apply the
patterns relevant to the chosen UI stack and app behavior.

The [official UI/shell evaluation](official-ui-evaluation.md) identifies the
current Template and shared-runtime foundations. Adapt colors, menus and layouts
while preserving the chosen shell's lifecycle, input and backend boundaries.
The demo's page names, palette and bar dimensions are implementation choices;
personal preferences remain separate from platform contracts.

## The constraints shape everything

- **Fixed 320×170.** Tiny and wide — design every screen for exactly this; nothing reflows. A few
  legible rows beat a dense grid. Don't cram.
- **Keyboard only.** No touch, no mouse. Navigation is keys. See [the keyboard](05-keyboard.md).
- **Tight, swapping RAM.** Keep assets small; don't hold big buffers.
- **LVGL 9.5** is the toolkit, drawing to the framebuffer. **Design in the desktop simulator first**
  (see [building and packaging](06-building-and-packaging.md)). Check fonts and bounds
  at 320×170, then qualify device input, performance and hardware separately.

## Use the MVVM + reactive structure

For apps built from the official LVGL Template, use its MVVM structure to keep
screens consistent and state predictable. Other stacks should follow their own
state/view conventions (see [architecture choices](03-architecture.md)):

- State lives in a model/viewmodel as **reactive subjects**; the view **binds** to them with the
  `reactive::bind_*` helpers instead of being poked imperatively.
- `BaseScreen` is the screen base; `BaseWidgets` the widget base. A `screen_manager` swaps the
  visible screen when the current-page subject changes.
- **Add a screen:** add a page enum, extend the model/viewmodel with a `show_<name>_page()`, create a
  `BaseScreen` subclass under `view/screens/`, register it in `screen_manager`. One screen = one
  file; the only central edit is one `switch` case.
- **Add a widget:** subclass `BaseWidgets`, implement `build()`, bind with `reactive::bind_*`.

## Consistent navigation is the biggest polish signal

Whatever navigation model you pick, make it **identical on every screen** — same keys, same
positions, same back behavior. That consistency is what separates "polished" from "slop." Two proven
approaches:

- **A fixed function-key lane / bottom bar** — a row of labelled chips mapped to fixed keys, where
  each chip always shows what its key does, so the user never guesses. Reserve it for actions that
  are otherwise hard to reach on a 46-key board — *not* for Enter/Esc, which are already easy.
- **A d-pad model** — map the device's arrow cluster (see [the keyboard](05-keyboard.md)) to
  up/down/left/right selection, Enter to act, and **Esc to go back everywhere** (hold Esc to
  quit/home).

Reuse *one* well-made list screen for every list (menus, item lists), rather than a different layout
per page.

## Forms, clear outcomes and persistent actions

A complete form can serve as its own review. Do not require another summary page
by habit when it only repeats values the user has just checked. Keep the primary
action, such as **1: Save**, in a fixed action lane outside the scrolling fields.
Show routine navigation under Help and in the user guide; reserve scarce footer
space for useful screen actions. Give the space back to content when no action
is needed. Keep the action label consistent with the actual destination (for
example, Save channel versus Save profile).

After scanning/importing, explicitly show success and the decoded item's name
before settings. A method label such as "QR/share link" and a count alone can
look like a reset. Distinguish "loaded into an unsaved form" from "saved"; preserve
local entries on validation errors and Back. Confirm the named saved result.

Validation and service-side preparation can run behind the Save action without
becoming a mandatory visible review step. Keep ownership, stale-state checks,
request correlation and cancellation before the first write. Ignore repeated
activation while busy; a held key must not skip a consequential confirmation or
save twice. Numeric shortcuts must remain ordinary characters inside text fields.

Reject invalid or unsupported actions with a concrete reason. For valid changes
with material side effects, use a brief, specific explanation/consent when needed
rather than repeating the whole form. A guide supplements clear UI; it does not
replace privacy choices. Physical risks that software cannot determine reliably
still need appropriate user instructions and narrowly scoped acknowledgment.

## Never block the UI thread

Long work — talking to a radio, a network call, shelling out to a tool — must **not** run on the
LVGL thread. A frozen screen reads as broken. Do the work on a bounded worker or in a
**resource-owning service when needed** ([architecture](03-architecture.md)), and marshal results back to the UI
thread using the toolkit's supported dispatch mechanism. Select the thread/process
boundary for this application's actual needs.

## Show what's happening

- **Stream long output** in a tail-following log pane that scrolls as results arrive, rather than a
  spinner that hides everything. It reassures the user and is invaluable for debugging.
- **A small persistent status bar** (radio/connection state, battery, an unread badge) lends a
  finished feel for very little code — read from `/sys`, refresh every few seconds.

Keep routine startup and reconnect preference synchronization quiet. Apply the saved
setting and return a correlated acknowledgment without a success toast; confirm
deliberate user changes when useful. Do not skip synchronization or suppress all
notices to hide one distracting message. Failures must remain visible. Test first
connection, reconnect, explicit changes, actual enforcement and error replies
separately; validate any optional quiet flag as a boolean.

## Theme: support light and dark

- Keep colors in **one constants file** — never hardcode a color per widget.
- Offer a **light/dark toggle** and make sure both are legible. At 320×170, contrast and font size
  matter more than cleverness. Test both themes in the simulator.
- Use **semantic color, not decorative** — screens ask for *meanings* (`warning`, `good-signal`,
  "the row you're on") and the theme maps them to pixels. Use a border
  consistently to indicate selection, and keep its meaning and contrast clear.

## Build screenshots into the app

Bind a key to dump the active screen to a PNG with a small confirmation toast. You need **320×170
PNG** screenshots for a Store listing (and your README) anyway, so have the app produce them itself —
it's the most authentic way to capture the real screens. (On the device, the framebuffer can also be
read directly from `/dev/fb0` for the same effect.)

## Errors and empty states

- Show failures **on screen, in plain words**, not just in the log. A hardware app that can't reach
  its device should say so and what to check ("camera busy; close the other camera app").
- Give empty states a line of guidance ("No notes yet — press Enter to create one"), not a blank panel.

## Accessibility and discoverability

Label important actions in plain words and provide a keyboard route to every
control, including scrolling information dialogs and dismissing overlays. Keep
focus visible. Pair color with text/shape so color alone does not identify a
failure, selection or privacy state. Check contrast in both themes and offer
readable text sizes within the actual glyph inventory. Do not hide the only hint
behind a long name or rely on a mouse/touch action on the device.

## Glyph discipline

Decide the font/glyph inventory per screen and make sure every character you render actually exists
in the font — a missing glyph renders as a tofu box and screams "unfinished." If you add icons
(e.g. from a symbol font), confirm the sizes you use are compiled in.

<a id="the-anti-slop-checklist"></a>

## UI checklist

Before you call it done:

- [ ] Consistent navigation on every screen; Esc always goes back; every action key labeled.
- [ ] Reads cleanly at 320×170 — legible font, not crammed.
- [ ] Both light and dark themes tested in the simulator.
- [ ] UI never freezes — all slow work off the LVGL thread.
- [ ] Long operations show progress; errors shown on screen in plain words; empty states guided.
- [ ] A status bar (connection/battery) present.
- [ ] A real icon (not the template default) and real 320×170 screenshots.
- [ ] No missing-glyph boxes anywhere.
- [ ] No placeholder/`TODO` text anywhere in the UI or metadata.


## Privacy state and asynchronous overlays

For asynchronous settings, show confirmed, Pending and Unknown states. Expire
pending actions after a deadline. Read back actual state when the underlying API
requires it; editing a cache is not confirmation. Use stable record/request IDs
and stop accepting a dismissed view's late results. A timeout can leave an outcome
unknown; it does not prove the backend rolled a write back.

Remove observers and timers with their owning views. Never hold an LVGL pointer
or a pointer into a reallocating vector across a worker callback or rebuild.
Keep global Help/Esc ownership explicit so input cannot reach a hidden editor.
Test navigation away, list reordering, repeated Return and disconnect while busy.

## First run and uncertain live data

Provide safe defaults, explain actual prerequisites, preserve existing data and
make consequential actions deliberate. Ask only for settings relevant to the app.
A local calculator may need no wizard. A hardware transmitter requires additional
consent described in its project section. Show actionable failure reasons.

Measurements need valid values, a meaningful timestamp and a freshness policy.
Show stale data as last known; unknown is different from zero. Coalesce updates
and refresh age labels. Device GPS and camera details belong in
[GPS/maps](projects/gps-and-maps.md) and [camera/QR](projects/camera-and-qr.md).

## Persistence and redraws

Debounce text saves by a pause in typing, flush at defined navigation/close
boundaries and keep rejected edits recoverable. Do not serialize local saves
behind unrelated slow hardware jobs. Quiet hours need local-time and midnight
semantics only if the app actually offers notifications.

Compare effective state before rebuilding object trees, while still handling
request completion and genuine changes. Preserve selection by stable identity
through reordering and define a consistent tie order. Prepare/index list data once
instead of repeating searches for every visible row. Measure realistic workloads;
a synthetic improvement is not a measured battery-life benefit.

Update selection styles and changed field values in place when layout is stable.
Avoid reconstructing every row on each arrow key or subscribing to several
subjects that each cause an identical initial rebuild. Preserve stable targets,
scrolling and observer ownership. If a selected record disappears, require a safe
explicit selection rather than silently acting on its replacement. Use small
shared visual helpers where they simplify actual callers; keep each screen's
confirmation, editing and resource lifetime explicit. Review cache ownership when
consolidating records: retaining large previews can extend their memory lifetime.
Selection helpers should not allocate unused styles on every unselected row.

Observe independent facts independently: a mode can change while connection
state stays Online. Refresh age/freshness and time-based filters even when no new
hardware event arrives. A presentation clock can update existing age labels and
markers without rebuilding the whole screen; bind its callbacks to screen/object
lifetime and test destruction as well as stale/future-time boundaries. Unknown
state must remain unknown after disconnect. Poll only the device facts actually
displayed. Measure operation counts separately from timing, using the same build
and data before/after; qualify device performance separately from host results.

## Keep context and keyboard help readable

Keep the current task/record in a bounded header and reserve the footer for short
keyboard hints or text entry. Truncate descriptive detail before information
needed to understand the action's target. Check real font/pixel bounds with long
names, selection, typing, scrolling and return navigation.

An LVGL outline can be clipped outside a tightly fitted parent. Use an inside
border or sufficient parent clearance. Keep border plus padding insets stable so
selection does not move text or resize the row. Verify both light and dark themes.

Group settings with nonselectable headings and give actions stable keys independent
of display order. Navigate through selectable actions; give long overlays scrolling
and an Escape path. Tests should find a setting by identity/label instead of a
historic number of Down presses, especially for privacy or destructive operations.

Detailed examples remain in [Mesh UI lessons](case-studies/mesh.md#ui-and-asynchronous-operations).
Next: [the keyboard](05-keyboard.md).

## Keep a complete setup in one place

When a task spans several settings, provide one shared setup flow with a local
draft across field editors and validation errors. Several entry points
can open the same flow; remove obsolete independent paths rather than keeping
duplicate implementations. Show which values belong to one item and which affect
the whole device. Imported settings can be suggestions without silently replacing
active configuration or device-specific calibration. Offer a separate saved
profile when that is useful, with its effect on the active session explicit.

On the small keyboard-driven display, keep the heading and primary action visible while
fields scroll. Update navigation selection in place. Test long errors,
UTF-8 byte limits, masked secrets, deep selection, both themes, Escape, repeated
Return, late replies and destroyed screens. Preserve an imported token when
returning to edit an unrelated field; closing setup should cancel the whole draft.

Separate local preparation, explicit Save, stored verification, live hardware
readback and actual connectivity/delivery. Cancellation before Save changes
nothing; once a write has started, explain that leaving cannot undo it. Report
partial success and uncertain outcomes explicitly so users do not duplicate an
operation. Mesh exercises this pattern in its unified channel setup; the pattern
also applies to network, peripheral and other device configuration tools.

## Task clarity and recovery

Keep related configuration in one task form with visible groups and a reachable
Save action. Identify whole-device changes; preserve edits on errors. The form
can be the review without a duplicate summary page. Reserve extra acknowledgment
for a specific irreversible, privacy or hardware consequence.

Use Cancel-first confirmation for irreversible deletion when Undo is not
available, binding the action to a stable identity rather than a moving row.
Explain communication outcomes in ordinary language; distinguish a transport
acknowledgment from a recipient receipt and a person reading the message. Make
important values readable in both themes and pair meaningful color with another
cue. Record scope/limits of search matching and qualify whole tasks rather than
claiming hardware success from screen renders. See the
[personal preferences](ui-preferences.md) for direct two-choice rows and grouped forms.
