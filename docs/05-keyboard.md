# 5. The keyboard

Input is keyboard-only, and the 46-key keyboard has some sharp edges that *will* cost you debugging
time if you don't know them up front. This chapter is the layout, the modifiers, and — most
importantly — the keycode reality your app has to handle to accept real text.

The raw-evdev decoder below is the C++/LVGL Template path. The shared cp0 SDK
already supplies a richer decoded keyboard-event contract; use one matching
backend and avoid translating its decoded characters a second time. Other
languages should implement/adapt the same behavior and independent fixture checks
at their own input seam. They need not embed a C++ library just to follow this guide.
See the [component comparison](components.md) and [prepared Template contribution](../contributions/template-keyboard/README.md).
The [current official-input evaluation](official-input-evaluation.md) records
reviewed sources, use/adapt decisions and the limits of the selected tests.

## The layout

46 keys, **no dedicated arrow keys**. Movement and symbols come from three modifiers:

- **Shift** → uppercase (and the standard shifted punctuation).
- **Fn** → the "orange" shortcuts: arrows, function keys, media, etc.
- **Sym** → the "blue" symbols printed on the keys (`?`, `!`, `@`, `#`, …).

Each modifier works three ways: **hold** it while pressing a key; **tap once** to apply it to the
next key only (sticky); **tap twice** to lock it on.

### Movement (Fn layer)

| Keys | Action |
|---|---|
| Fn + F / X / Z / C | Up / Down / Left / Right |
| Fn + K / N | Home / End |
| Fn + L / M | PageUp / PageDown |
| Fn + Backspace | Delete |
| Hold Esc | Back to the home screen |

Function keys are `Fn + 1…0` (F1–F10), `Fn + O / P` (F11/F12). Useful ones: `Fn + H` (app help),
`Fn + J` (screenshot). So **`Fn + F / X / Z / C` is your d-pad** — that's the arrow cluster your UI
navigates with.

## Use the official map, not a hand-built approximation

The authoritative references are:

- [M5Stack key specifications](https://github.com/CardputerZero/cardputerzero.github.io/blob/main/docs/en/CP0_keys.md): printed legends, Fn functions and hold/one-shot/lock behavior.
- [Official launcher symbol decoder](https://github.com/CardputerZero/launcher/blob/4c05b444cb977cb90e2f33eb4c8261226e370713/ext_components/cp0_lvgl/src/cp0/cp0_keyboard_keymap.c): the complete 32-symbol map, with a runtime override from `/usr/share/keymaps/tca8418_keypad_m5stack_keymap.map`.
- [Official Keyboard Guide input](https://github.com/CardputerZero/Keyboard-Guide/blob/main/src/input/keyboard_guide_input.cpp): examples of version-dependent modifier-state reporting. Check which kernel interface exists on the target image before adopting a backend.

**Correction, 2026-11-16:** an earlier version of this chapter said there was no
published table and supplied 14 assignments. Three were wrong (`92` was shown as
colon, `80` as minus and `71` as slash), and 18 symbols were missing. The worked
example inherited those errors. The device's installed map and the official
launcher agree on all 32 assignments below. Do not reuse the old table.

| Linux event code | Symbol | Linux event code | Symbol |
|---|---|---|---|
| 26 | `!` | 27 | `@` |
| 39 | `#` | 40 | `$` |
| 41 | `%` | 43 | `^` |
| 51 | `&` | 52 | `*` |
| 53 | `(` | 94 | `)` |
| 55 | `~` | 69 | backtick |
| 70 | `_` | 71 | `-` |
| 72 | `+` | 73 | `=` |
| 74 | `[` | 75 | `]` |
| 76 | `{` | 77 | `}` |
| 79 | `;` | 80 | `:` |
| 81 | apostrophe | 82 | double quote |
| 83 | `<` | 85 | `>` |
| 86 | backslash | 89 | vertical bar |
| 90 | `,` | 91 | `.` |
| 92 | `/` | 93 | `?` |

These are **Linux event codes**, not ASCII values, matrix positions or XKB codes
(which use an offset). For example, Sym+N produces the symbol-layer code for
slash, `92`; translating `92` to `:` was an application error.

## A reusable input component

The worked example supplies a reusable C++ decoder and regression suite:

- [keyboard_decoder.h](https://github.com/Prophet60191/m5stack-cardputer-zero-mesh-app/blob/f1c2c77b9ccb1a26ff366539af7d51f371a3e8af/src/platform/keyboard_decoder.h)
- [keyboard_decoder.cpp](https://github.com/Prophet60191/m5stack-cardputer-zero-mesh-app/blob/f1c2c77b9ccb1a26ff366539af7d51f371a3e8af/src/platform/keyboard_decoder.cpp)
- [independent vendor fixture](https://github.com/Prophet60191/m5stack-cardputer-zero-mesh-app/blob/f1c2c77b9ccb1a26ff366539af7d51f371a3e8af/tests/fixtures/cardputerzero-keymap.map)
- [raw-event/editor tests](https://github.com/Prophet60191/m5stack-cardputer-zero-mesh-app/blob/f1c2c77b9ccb1a26ff366539af7d51f371a3e8af/tests/keyboard.cpp)
- [LVGL/evdev integration](https://github.com/Prophet60191/m5stack-cardputer-zero-mesh-app/blob/f1c2c77b9ccb1a26ff366539af7d51f371a3e8af/src/platform/linux_input.cpp)

For a Template/raw-evdev app that needs this extension, keep the component and
tests together after evaluating current official options. A shared-runtime app
should consume its official decoded input contract instead of adding this decoder.
Pin the source revision when copying or vendoring, preserve MIT/M5Stack attribution,
and keep the fixture's upstream provenance. The component has no radio, filesystem or UI-object
ownership; its caller supplies raw event code/value and current typing context.
It returns a character or semantic control plus press/release state. The LVGL
adapter owns device discovery, trusted keymap-file I/O, routing and repeat timing.

### The driver already selected the Sym layer

On the built-in `tca8418c` keyboard, look up a symbol-layer code in the official
map **before ordinary US key translation**. Do not require a physical Sym-down
flag to recognize it. The driver can emit that same selected symbol after a
single tap, under lock, or after the app opens while Sym is already active.
Reconstructing a second modifier state machine for already-translated symbols
can apply the layer twice or discard valid symbols.

Scope this table to the identified built-in keyboard. A USB keyboard's code 26
normally means `[`, while the CardputerZero's selected symbol code 26 means `!`.
Applying the vendor table globally corrupts standard keyboards. The worked
example's generic profile is US-layout input; use a qualified xkbcommon backend
if an application needs additional layouts or composition.

Keep Shift/Control/Alt state **per input device**. Preserve each key's press-time
translation until its release, even if a modifier is released, the keymap changes,
or the editor closes in between. Initialize/resynchronize available kernel state
after opening a device or losing events; do not invent support for a modifier-state
API that the installed kernel does not expose. Older images and newer vendor
sources have different interfaces. No app needs to force access to shared I2C
hardware merely to decode these already-selected symbol codes.

### Separate text from Fn actions

Fn arrow/Home/End/Delete codes are semantic controls, not printable characters.
Help, Screenshot, PageUp/PageDown, Insert, F1-F12 and media/display actions must
also remain non-text. Define what your app does with each one; an unbound action
must be consumed safely rather than encoded as garbage in a draft. A one-line
editor need not invent a PageUp or Insert action. System-wide media/display keys
may also be handled by the platform; do not add duplicate shell-outs per app.

Global Help/Screenshot should remain reachable while editing. A visible Help
popup owns input: Enter must not send the draft underneath it. Closing help must
restore the same editor, text and cursor.

**Consume shortcuts before LVGL delivers them to the focused widget.** Returning
`true` from your application's callback does not automatically prevent LVGL from
sending the key onward. The worked example filters each new press/release in the
indev read callback and exposes only unconsumed input to LVGL. Use the same route
for simulator and device input; test that shortcut values never become text.

### Stream handling and focus timing

- Query the current typing context for **each event**, not once per frame. Enter
  can open an editor and a letter can follow within the same evdev batch.
- Store active translations per device. Handle overlapping letter presses without
  dropping the second character or treating an older release as a newer release.
- Choose one repeat owner (LVGL in the worked example); do not also replay Linux
  repeat records. Repeated Enter must never queue several sends.
- On `SYN_DROPPED`, discard records until `SYN_REPORT`, cancel stale holds and
  resynchronize available modifiers. A lost Escape release is not an app exit.
- EOF/disconnect must release stale input and leave the reader inert. Do not
  perform a blocking retry loop on the UI thread.

## Required regression coverage

Compile the production decoder on the development host too; hiding it under
`!USE_DESKTOP` prevents simulator tests from exercising it. On Linux, the worked
example additionally feeds synthetic `input_event` records through the **real
evdev reader, shortcut filter, LVGL indev and focused textarea**, using a pipe.
There is no `/dev/input` injection, RF or live user typing in that suite.

Cover every official symbol against an **independent upstream fixture**; ordinary
letters and Shift; driver-selected symbols with held/released/locked modifiers;
Fn cursor/Home/End/Delete; Help/Screenshot while editing; unbound Fn keys; key
release order and rollover; same-batch focus changes; multiple device profiles;
malformed/partial keymaps; event loss and disconnect. Check draft text and cursor,
not only that a handler ran. Retain source/hash evidence for the fixture; never
change both expected data and implementation solely to make a failing test pass.
Verify the fixture is tracked in a clean checkout: templates often ignore `*.map`
as linker output, so a deliberate exception is needed for a keymap fixture.

Automated event replay validates the software contract. A physical check can
confirm a particular device/image's emitted events and ergonomics, but is not
needed to rediscover an already-published mapping. Record those results separately
and recheck compatibility when the kernel/keyboard firmware changes. Reading a
shared evdev stream does not require stopping the launcher or grabbing the device;
any diagnostic capture should be bounded and use synthetic input only.

## A nicety: let the d-pad keys navigate without Fn

The bare `F / X / Z / C` keys type letters, but outside a text field there's nothing to type — so
many apps feel better if the bare `F/X/Z/C` keys act as the **d-pad** everywhere *except* while a
text field is focused, and require Fn for the arrows only inside text entry. (Both still work: the
Fn-translated `KEY_UP`/etc. keep functioning.) Switch on whether a text input is currently capturing.
It removes the need to reach for Fn just to move around a menu.

---

Next: the full build-and-ship pipeline — [building and packaging](06-building-and-packaging.md).


## Bound input work and clean up the owning device

A native input reader should budget raw read attempts across the complete
`continue_reading` chain, including ignored records, modifiers, repeats and
interruptions. A limit on decoded characters alone does not bound that work.
Yield on exhaustion and retain queued/pending input for the next poll. Verify both
modifier floods and ordinary typing across the boundary without loss/duplication.

Associate a pending hold action with its source input device. EOF, lost input and
object teardown should cancel that owner's timer without synthesizing a short
release/click. An unrelated device's release or deletion must not cancel the
current owner's hold. Use the same cleanup contract for native and simulator
adapters. Test two devices using the same key, owned deletion, loss/disconnect and
simulated time passing after cleanup. Mesh's current component uses 128 raw read
attempts per device poll; that is a scoped fairness bound, not a global timing guarantee.
