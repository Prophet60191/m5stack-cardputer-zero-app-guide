# Worked example: Mesh and the lessons it contributed

Mesh is one application built with a native LVGL UI and a Python radio service.
Its channels, acknowledgments, private-channel keys and persistence policy explain
many of this guide's original examples. They are optional application concerns.
A calculator or local notes app does not need the radio service or its firewall.

## Evidence and scope

The preserved sections below come from the [previous guide revision](https://github.com/Prophet60191/m5stack-cardputer-zero-app-guide/tree/a7ddc7ff73e71a32c71b68bbc87290af73424eea),
reviewed 2026-11-16. Their detailed wording is retained to avoid losing the failures
that motivated the general rules. Read them as Mesh-specific examples, alongside
[architecture choices](../03-architecture.md), [project sections](../projects/README.md)
and the [lesson index](../lesson-index.md).

Implementation and evidence are in the pinned [Mesh source](https://github.com/Prophet60191/m5stack-cardputer-zero-mesh-app/tree/c51a45ee61813bf9685766f9f45c95e6778780a5),
[remediation record](https://github.com/Prophet60191/m5stack-cardputer-zero-mesh-app/blob/c51a45ee61813bf9685766f9f45c95e6778780a5/docs/review-remediation.md),
[keyboard checks](https://github.com/Prophet60191/m5stack-cardputer-zero-mesh-app/blob/c51a45ee61813bf9685766f9f45c95e6778780a5/docs/keyboard.md)
and [maintenance measurements](https://github.com/Prophet60191/m5stack-cardputer-zero-mesh-app/blob/c51a45ee61813bf9685766f9f45c95e6778780a5/docs/maintenance-pass.md).
The candidate has 98 backend tests plus native and package checks. Those results
qualify that application/revision, not every future app or all official services.
Outdoor GPS, live public-peer interoperability and physical IPv6 qualification
remain separate gaps; simulated events do not constitute a physical all-key sweep.
No new device qualification is claimed by reorganizing this guide.

## Subsequent modularity and input maintenance

Mesh 0.1.11 adds bounded input polling and source-owned hold cleanup. The
[architecture decision](https://github.com/Prophet60191/m5stack-cardputer-zero-mesh-app/blob/f1c2c77b9ccb1a26ff366539af7d51f371a3e8af/docs/architecture.md)
explains its purpose, benefits, costs and official-platform compatibility. The
[M5Stack review package](../../submissions/m5stack-2026-11-16/README.md) keeps this
maintenance separate from the optional Template integration. The original lesson
blocks below remain preserved at their stated source revision.

## Subsequent GPS integration qualification

The [2026-11-23 GPS record](https://github.com/Prophet60191/m5stack-cardputer-zero-mesh-app/blob/cd82b8ce24a1cab1ef68369e744a508c4ac887ef/docs/internal-gps-validation.md)
supersedes the earlier outdoor-GPS gap for that fitted receiver and exact versions.
App 0.1.17 refreshes exported local-node snapshots without enabling location
broadcasts. A separate pinned Meshtastic native-service patch extends its ATGM
identification window from 500 to 1500ms after seven of eight measured replies
arrived later than 500ms. The driver had suppressed normal output before probing.
That is a measured third-party integration problem, not an official GPS-app defect.
Its reserved nonce, 30s snapshot interval and two-minute freshness policy are
Mesh-specific, not defaults for other GPS apps. The general [GPS section](../projects/gps-and-maps.md)
explains the transferable cache, ownership, privacy, timing and qualification lessons.

## Subsequent everyday-use refinement

Mesh 0.1.15's [implementation](https://github.com/Prophet60191/m5stack-cardputer-zero-mesh-app/tree/5f0bc3ee80ff3b8bd1cfa6e496999dac6e8edc29)
and [qualification record](https://github.com/Prophet60191/m5stack-cardputer-zero-mesh-app/blob/0b63be648324d47581963b8fe535ae5ba6060ce8/docs/usability-refinement.md)
provide later evidence for readable editor states, stable Cancel-first deletion,
grouped forms, explicit saved-setup consequences and English case-insensitive
search. The installed candidate passed its native/backend/package gates,
ordinary-user synthetic device replay and the owner's specified physical checks.
Those checks did not add powered-radio, public-peer or outdoor GPS qualification.

The upgrade also demonstrated why files and running processes must be checked
separately: the existing service still reported the old version until restarted
through its normal lifecycle. A GUI version-query attempt opened a UI because
that option was unsupported; the temporary instance was stopped. The general
[build/install guidance](../06-building-and-packaging.md#automate-the-matching-package-build)
records safer verification and preservation checks. These results qualify the
named Mesh revision, not a reusable library or another application's hardware.

## Architecture and state

### Make the boundary authoritative

The UI may show a local message echo, but the supervisor must retain its actual
status. Store ACK/NAK results before broadcasting; a reconnect snapshot must not
turn Delivered back into Sending. Retries need a stable message ID plus a new
attempt token so an old ACK cannot complete the new attempt. Apply retention to
existing history immediately, broadcast removals, and bound total history even
when a user chooses “All.” Reapply persisted client preferences on reconnect and
define which client wins if multiple clients choose different policies.

Every asynchronous result needs identity: a request ID plus the target channel,
node or record ID. Indexing a refreshed vector is unsafe across callbacks. Capture
stable IDs, resolve them again before acting, and cancel acceptance when a user
dismisses the pending overlay. This applies especially to secret-bearing results
such as share codes: a hardcoded group name can disclose another group's key.

### Preserve identity and durable intent safely

A slot or vector index is a location, not an identity. When configuration can
replace its contents, bind conversations, drafts, selections, retries and commands
to a stable identity and validate it at the owner before acting. For secret-bearing
configurations, use a keyed local digest rather than exposing the secret or a
brute-forceable plain hash. Moving the same logical record can preserve identity;
changing its key/name should archive old context instead of silently rerouting it.

Keep bounded durable history authoritative in the supervisor. Commit ACK/failure,
retention and deletion changes before publishing snapshots. Persist drafts without
turning them into a replay queue. An interrupted send should become Failed after
restart, with an honest uncertainty reason. Distinguish acceptance by an API, a mesh
acknowledgment, a recipient acknowledgment and a read receipt; never infer a later
stage from an earlier one. Confirm the acknowledgment source before naming a recipient.

If opting out of disk history retains an active RAM session, define what opting
back in saves. Persist its existing drafts without requiring another keystroke;
test an immediate restart after the preference change and notify every client.

For related preference files, record and sync a complete validated transaction,
then roll it forward idempotently after interruption. Applying a saved hardware
profile must not restore transmission or privacy consent as a side effect.

Exercise the real event library when testing callback registration. A child topic
can inherit required arguments from its parent; changing one listener's optional
parameters can make another subscription fail during startup. Register the same
parent/child listeners as production and deliver representative events. Count
remote RF reception from received packets, rather than local admin replies or
cached node-update notifications.

Audit greeting builders as part of the live control path. Send one bounded
history snapshot, avoid redundant client requests, and perform slow dependency
probes outside lifecycle locks. Cache informational version queries while forcing
a fresh compatibility check before hardware starts. Fresh security verdicts need
their own age policy. Capture shared interface references and guard every library
dereference when constructing status, even if most callers already hold a lock.

## UI and asynchronous operations

### Privacy state and asynchronous overlays

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

### First run and uncertain live data

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

### Keep context and keyboard help readable

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

## Radio route validation

- **Validate every route to an RF action.** A DM destination does not bypass
  channel validation. Reject broadcast aliases disguised as destinations. Check
  real key formats and public/private classification, not just a channel name.
  Supporting public channels is compatible with a secure client: use clear labels,
  explicit selection, and separate location opt-in. Enabling location on one
  channel must not also enable another.
  Preserve channel identity through pickers, details, intents and share replies.

## Licensing choices in this application

- **Mind the copyleft.** The Meshtastic stack (`meshtasticd`, the `meshtastic` Python library) is
  **GPL-3.0**. If any of your *code* links a GPL library in-process, that code must be
  GPL-compatible. A clean, real-world split:
  - Your **C++/LVGL UI stays MIT** — it only talks to the other process over a socket (separate
    program; preserve the distinct licenses and interfaces).
  - The supervisor incorporates the GPL client library and is licensed **GPL-3.0-or-later**.
  - **This example does not bundle the daemon/library** in its `.deb`; its GPL
    supervisor sources are included. The daemon/library are installed separately
    using documented versions. This is the example's dependency plan, not a rule
    that all apps must use external prerequisites or that GPL forbids bundling.
    See the [three dependency plans](../06-building-and-packaging.md#packaging-a-python-app).
  - Running a separate GPL *program* as a subprocess (e.g. launching `meshtasticd`) does **not**
    by itself determine the other program's license; the nature of the integration
    and applicable terms still matter. The example publishes both components as
    open source with explicit licenses.
