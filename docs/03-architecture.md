# 3. An architecture that works

This is the most important chapter. The shape you choose here determines whether your app feels
native, stays within the RAM budget, is testable, and is *safe*. The recommendation is specific:

> **A native C++/LVGL UI for the look, and — if your app touches real hardware or does privileged or
> long-running work — a separate "supervisor" process that owns that, talking to the UI over a small
> local socket using *intents*.**

The worked example (the Mesh app) is built exactly this way, and it's what the rest of this chapter
explains.

## Why native LVGL for the UI

There are three ways people draw UIs on this device:

1. **Native C++/LVGL** — a compiled binary draws LVGL widgets to the framebuffer. This is what the
   built-in apps and the official template use.
2. **Pure-Python self-drawn** — a Python TUI rasterized to the framebuffer by hand. It can be
   genuinely polished, but as a *retro-terminal* aesthetic, and the interpreted render stack is slow
   and RAM-hungry on this CM0 (tens of milliseconds per keypress unless you engineer around it).
3. **Native LVGL UI + a Python helper** — the compiled binary for the look, a Python process for
   logic. Right architecture; this guide's recommendation.

On *this* hardware the constraints decide it. Only LVGL reads as native (proportional fonts,
anti-aliased widgets, smooth scrolling, matching the launcher). LVGL's compact C structs and
dirty-region redraw win decisively on the two axes that hurt most under tight, swapping RAM —
startup and resident set. A Python-drawn UI buys multi-board portability you don't need for a
device-specific app, at a cost in look and memory you can't spare.

**So: native C++/LVGL for anything you want to look like it belongs on the device.**

## Why a separate supervisor

Here's the key insight. Your *UI* wants to run on your laptop (in the simulator) and stay simple and
crash-safe. But the interesting work — driving a radio, powering a Cap, shelling out to a tool,
holding a network connection — is slow, privileged, or hardware-bound, and *can't* run in the
simulator. Jamming it into the UI binary makes the UI un-simulatable, fragile, and hard to keep
least-privilege.

So split it: the **UI never touches hardware directly.** A second process — the **supervisor** —
owns everything hardware/privileged/long-running, and the two talk over a local Unix socket.

```
 ┌─────────────────────┐   newline-JSON    ┌──────────────────────┐
 │  C++ / LVGL UI       │   intents  ──────▶│  supervisor          │ ──▶ hardware / daemon / network
 │  (what you see;      │◀──────────  events│  (owns the risky     │     (radio, Cap, a tool, a socket)
 │   simulator-runnable)│   Unix socket     │   stuff)             │
 └─────────────────────┘                   └──────────────────────┘
```

This one decision buys you an unusual amount:

- **The UI is simulator-runnable.** With the supervisor stubbed (or simply absent), every screen is
  fully usable on your laptop. You iterate in seconds, and only flash to the device to confirm.
- **Least privilege falls out naturally.** The privileged/hardware code is a small, separate,
  auditable process. The UI needs no special rights.
- **Process ownership can be explicit.** Kernel exit releases file descriptors and
  GPIO requests, but does not restore sysfs power/mux values or kill detached
  descendants. A `finally` block cannot handle SIGKILL. Use a guardian that detects
  parent death through a pipe, stops/reaps the daemon, then restores hardware;
  add service control-group cleanup for simultaneous kills. Test that sequence
  with real subprocesses and fake hardware before trusting it on the device.
- **Exclusive ownership is deliberate.** Hold an advisory `flock` for the whole
  supervisor lifetime, before replacing its socket or recovering hardware. The
  kernel releases the lock on exit; the file may remain. A stale PID file or a
  broad `pgrep -f` kill is not an ownership mechanism.
- **It stays testable.** The supervisor can expose a mock, and the UI can't accidentally reach past
  the boundary.

The supervisor is usually **Python** — that's where the mature libraries live (for a radio app, the
Meshtastic client library; for other apps, whatever drives your peripheral) and it's easy to test on
the device on its own, over the socket, before any UI exists.

## Intents, not mechanism

The rule that makes the boundary *safe*: **the UI sends intent, never mechanism.**

The UI sends `{"intent":"radio.start"}` or `{"intent":"message.send","text":"…","channel":1}` — a
named action with data. The supervisor maps each intent to **one fixed, validated action**. The UI
*never* sends a command string, a path, or anything the supervisor executes verbatim.

Why it matters: a compromised or buggy UI can only ask for actions you've explicitly defined and
validated — it can't ask the privileged side to run an arbitrary command. The privileged process
treats everything it receives as untrusted input and re-validates it. (This is also just good
design: a new feature is a new intent + event, and nothing in the core changes.)

A minimal protocol: newline-delimited JSON over a Unix socket. The client sends **intents**; the
supervisor sends **events** — both as replies and asynchronously (an incoming message, a status
change). Keep it small and documented. The worked example's full protocol is a good template to
copy.

## The MVVM shape of the UI

The LVGL side follows **MVVM + reactive binding**, which the official template already sets up:

- **model** — plain application state.
- **viewmodel** — presentation logic; exposes **reactive subjects** (wrappers around LVGL's
  `lv_subject`/`lv_observer`).
- **view** — the LVGL screens and widgets, which **bind** to the viewmodel's subjects.

Data flows model → viewmodel → view by binding, so a state change updates the screen automatically;
the view sends user actions back as events (and, for anything hardware-bound, the viewmodel emits an
*intent* to the supervisor). **Bind, don't poke** — never mutate widgets imperatively from logic.

A `screen_manager` owns the screens and switches the active one when a "current page" subject
changes. Adding a feature later is: add one screen file, register it, and (if it needs hardware) add
one intent. Nothing else changes. The details are in [UI and polish](04-ui-and-polish.md).

## Separate the device facts from the app logic

One more durable idea, worth building in even for your first app: keep **device-specific facts as
data**, isolated behind a seam, and resolved once at startup — so your render loop and logic never
branch on hardware particulars. The two seams are:

- **The board's wiring** — SPI bus/CS, the reset/busy/IRQ pins, the power/routing switches, the
  GNSS port — as one frozen record, resolved by a cheap presence probe. (Resolve the gpiochip by
  kernel *label*, not number — the number moves across CM revisions.)
- **The display/input surface** — the screen's size and colour depth, the keyboard layout — as
  another record, bound once.

If you expect to build more than one app (or support more than one board), this is the line between a
reusable **toolkit** (both seams + core resource interface + the child-process boundary + the
simulator) and the **app** (your concrete screens and features). You don't need a full toolkit on day
one, but keeping hardware facts as isolated data, and everything talking to a hardware *interface*
with a mock behind it, is what makes off-device development and tests possible later.

---

Next: making the UI itself feel finished — [UI and polish](04-ui-and-polish.md).

## Make the boundary authoritative

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

## Preserve identity and durable intent safely

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

For related preference files, record and sync a complete validated transaction,
then roll it forward idempotently after interruption. Applying a saved hardware
profile must not restore transmission or privacy consent as a side effect.
