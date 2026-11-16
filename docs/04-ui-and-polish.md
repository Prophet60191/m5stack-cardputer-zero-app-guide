# 4. UI and polish

What makes a CardputerZero app feel finished instead of thrown together. None of this is hard; it's
mostly consistency and a handful of patterns applied everywhere.

## The constraints shape everything

- **Fixed 320×170.** Tiny and wide — design every screen for exactly this; nothing reflows. A few
  legible rows beat a dense grid. Don't cram.
- **Keyboard only.** No touch, no mouse. Navigation is keys. See [the keyboard](05-keyboard.md).
- **Tight, swapping RAM.** Keep assets small; don't hold big buffers.
- **LVGL 9.5** is the toolkit, drawing to the framebuffer. **Design in the desktop simulator first**
  (see [building and packaging](06-building-and-packaging.md)) — it renders the real UI at 320×170,
  so what looks right on your laptop looks right on the device.

## Use the MVVM + reactive structure

The official template's structure *is* most of the polish, because it keeps screens consistent and
state predictable (the shape is in [the architecture chapter](03-architecture.md)):

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

## Never block the UI thread

Long work — talking to a radio, a network call, shelling out to a tool — must **not** run on the
LVGL thread. A frozen screen reads as broken. Do the work on a reader thread or (better) in the
**supervisor process** ([architecture](03-architecture.md)), and marshal results back to the UI
thread (LVGL's `lv_async_call`, or your supervisor-event poll). This is also *why* the supervisor
split exists.

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
  "the row you're on") and the theme maps them to pixels. A colored border is "one more color with no
  meaning"; keep borders neutral and reserve color for meaning.

## Build screenshots into the app

Bind a key to dump the active screen to a PNG with a small confirmation toast. You need **320×170
PNG** screenshots for a Store listing (and your README) anyway, so have the app produce them itself —
it's the most authentic way to capture the real screens. (On the device, the framebuffer can also be
read directly from `/dev/fb0` for the same effect.)

## Errors and empty states

- Show failures **on screen, in plain words**, not just in the log. A hardware app that can't reach
  its device should say so and what to check ("antenna attached? Cap seated?").
- Give empty states a line of guidance ("No nodes yet — waiting for the mesh"), not a blank panel.

## Glyph discipline

Decide the font/glyph inventory per screen and make sure every character you render actually exists
in the font — a missing glyph renders as a tofu box and screams "unfinished." If you add icons
(e.g. from a symbol font), confirm the sizes you use are compiled in.

## The anti-slop checklist

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

---

Next: the keyboard — and the one part of input that will bite you if you don't handle it —
[the keyboard](05-keyboard.md).

## Privacy state and asynchronous overlays

Render device settings as confirmed values, Pending, or Unknown. Do not optimistically
flip a privacy boolean before the supervisor/device confirms it; an offline “Off”
can mislead someone carrying a radio. Use request IDs and a deadline, and expire
pending state if the response never arrives. Configuration cache writes are not
readback. Make the target explicit when enabling behavior on one channel/group.

An overlay awaiting a result must stop accepting that result after Esc, navigation
or teardown. Match the response to both request and target. Use stable record IDs
across list rebuilds, never pointers into a vector that can reallocate. Tie LVGL
observers to an object's lifetime or explicitly remove them. Regression-test list
reordering while details or an action menu is open.

Apply deadlines to every waiting view, including generic service operations.
Timeout or disconnect means the result may be unknown; do not claim a write was
rolled back. Clear request acceptance on dismissal, echo valid IDs on validation
errors, and ignore repeated Return while busy. Keep request correlation fields
separate from the object being changed (for example, request `id` and target
`message_id`).

## First run and uncertain live data

A complete first run needs a safe default, a reviewable configuration, dependency
failure messages, and a separate deliberate step to enable hardware transmission.
Never overwrite an existing profile to make the wizard succeed. Show receive-only
separately from disconnected and transmitting states. Surface the actual stop
reason in diagnostics instead of hiding every failure behind a generic Error.

Treat GPS data as a measurement with a timestamp. Validate finite coordinates,
bounds, clock plausibility and freshness at the owner, even if the UI displays a
marker. Coalesce telemetry updates and refresh age labels; a cached location must
not look like a new fix. Debounce draft persistence to avoid a disk transaction on
every keystroke, flush on navigation, and keep rejected sends editable. Quiet hours
need explicit local-time semantics and a window that works across midnight.

Keep a conversation registry independent of messages. Draft-only, pinned and
cleared conversations must remain reachable after rebuilding the list; deleting
the conversation must remove that saved state too. Bind a DM draft to both peer
and selected channel, so a channel change cannot move unsent text to another mesh.

Distinguish enabling the GPS receiver from consenting to location broadcasts.
A timestamp without valid coordinates is not a fix. Show stale/unknown locations
as last known, and test an actual clear-sky fix separately from parser validation.

Test the actual camera stack. A CSI sensor's `/dev/video0` may be a raw sensor/ISP
node, not a webcam stream. On the stock image, use a fixed libcamera/rpicam capture
command with bounded dimensions/time and decode in memory; do not save private
camera frames merely to test a scanner. Missing decoder libraries and camera-busy
failures should produce actionable UI errors, not a misleading "no QR found."
Measure capture startup on the device before choosing the deadline; include
startup, exposure and decoding within a bounded total budget.

Give a camera operation a ready state with an explicit keyboard action such as
`Return: scan`. Publish a visible busy state before dispatching asynchronous work,
ignore repeated Return while busy, and show success or an actionable retry after
the matching result. Correlate replies by request ID; dismissed or superseded
results and unsolicited state updates must not replace a newer view. Clear cached
results when starting a new request. On disconnect, explain that the result is
unknown if the operation could already have changed state. If Escape only leaves
the view, say so; do not imply that it cancels hardware work or rolls back an
import. Keep simulator limitations in development docs instead of user prompts.

When scanning can lead to configuration changes, separate capture, preview and
commit. Keep the decoded secret on the backend, return a nonsecret preview, and
require a Cancel-first confirmation. Bind its short-lived token to the requesting
connection and the exact configuration shown. Changing configuration, Escape or
teardown must invalidate the preview, including work still queued on the server.
Give one bounded camera job a cancellation event and own its helper/child process
group. Keep capture off the serialized radio worker; commit radio writes there
only after confirmation. Announce committed results if their view has been left.

Measure queue pressure with the actual debounce semantics. A 650 ms typing-pause
debounce is different from a periodic write every 650 ms. Local draft/history
commits should not wait behind camera/admin work: serialize local state with its
own lock while preserving explicit persistence-barrier ordering. Test that local
writes and radio status still progress while the slow operation is blocked.

Compare effective state before rebuilding LVGL object trees. A draft echo can be
identical to the local value; merge pending local edits first and still process
request completion even when no redraw is needed. Genuine pin, deletion and
history-preference changes must continue to notify observers. When a list is
rebuilt, preserve its highlighted identity through reordering and define a stable
tie order. Prepare typed rows with one indexed pass before rendering; search the
history once instead of once per conversation.

## Keep context and keyboard help readable

On a 320x170 screen, keep the active channel/target in a fixed conversation
header and reserve the footer for short keyboard hints or compose input. Bound
long names and preserve the routing identity and privacy label before truncating
the less critical text. Check actual pixel bounds with the real fonts, including
long peer names, message selection, composing, scrolling and returning to the list.

Render selection lines in both themes. An LVGL outline sits outside an object's
bounds and can be clipped by a tightly fitted parent. Use an inside border or
reserve clearance through the parent chain so the entire line stays visible.
When adding a border, account for its width in the content inset; keep the sum of
border and padding stable so selection does not move the text or resize the row.

Give settings stable action keys independent of display order. Group related
options with nonselectable headings; navigation should visit actual settings
only. Tests should find the selected label rather than blindly pressing Down a
historic number of times, especially before transmission or privacy actions.
Long information overlays need keyboard scrolling as well as an Escape path.
