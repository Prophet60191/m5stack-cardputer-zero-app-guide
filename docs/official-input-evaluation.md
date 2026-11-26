# Official keyboard/input evaluation

Reviewed 2026-11-18 under the [library principles](library-principles.md).
Decision: **use the official shared input backend for apps built on that runtime;
adapt the official Template where its input subset does not meet the app's needs.**
Defer a standalone general keyboard library. The existing portable decoder is a
candidate Template extension, not a replacement keyboard standard.

## Current official sources

These default-branch heads were checked live. The
[evidence manifest](official-input-evaluation-evidence.json) records exact file
hashes and selected test results. These are source revisions, not claims about
the libraries or firmware installed on a particular device.

| Source | Reviewed revision | Relevant evidence |
|---|---|---|
| [Official key specifications](https://github.com/CardputerZero/cardputerzero.github.io/blob/eeb3c9f61afc33cc1ceb33f3ed0b81fd95491c0b/docs/en/CP0_keys.md) | `eeb3c9f61afc33cc1ceb33f3ed0b81fd95491c0b` | Modifier modes, Fn functions, recommended action keys and navigation aliases |
| [Template input](https://github.com/CardputerZero/Template/blob/477fa6d217b683e3084c361a757f03dc8ca9f753/src/platform/linux_input.cpp) | `477fa6d217b683e3084c361a757f03dc8ca9f753` | Native mapper and evdev delivery; same revision as the prepared proposal base |
| [Shared runtime contract](https://github.com/CardputerZero/launcher/blob/13d2f26b103e5c9292be7287bc640df9adf6faeb/docs/current-implementation-and-components.md#input-delivery-contract) | `13d2f26b103e5c9292be7287bc640df9adf6faeb` | Native navigation versus structured text/modifier events; ownership and build path |
| [Keyboard Guide input](https://github.com/CardputerZero/Keyboard-Guide/blob/dd0c1bf630ce2eabaca218417763a66fa8efe1cc/src/input/keyboard_guide_input.cpp) | `dd0c1bf630ce2eabaca218417763a66fa8efe1cc` | Diagnostic input and modifier-state backends |
| [AppBuilder starting instructions](https://github.com/CardputerZero/AppBuilder/blob/18996b694ae305306fc5d457d982cfba0b0e7cc5/README.md#starting-a-new-app) | `18996b694ae305306fc5d457d982cfba0b0e7cc5` | Scaffolds the current Template; later upstream changes are manually adopted |

Template PR [#4](https://github.com/CardputerZero/Template/pull/4) remains open
and unmerged at this review. Its existence does not change the current base or
establish acceptance of my separate prepared proposal. No upstream contact occurred.

## What the official approach provides

**Guidance:** hold/one-shot/lock modifier behavior and Fn actions are already
specified. Bare F/Z/X/C as arrows outside text entry is an official recommendation,
not a new layout invented by my apps. The specification recommends aligned 4–8
action hints and also allows other keys with visible explanations. My footer
preferences should be evaluated against that guidance during visual design;
they are not a reason to alter the physical keymap.

**Template:** `map_evdev_key()` at lines 186–215 handles Escape, Left/Right, Z/C,
4–8, Screenshot and Help. It is a navigation subset, not a complete text-entry
adapter: ordinary letters and the full Sym map are absent. A text-heavy app
scaffolded from it still needs input integration. AppBuilder copying the latest
Template does not add that missing behavior. This is an integration limitation
for my use case; the review does not establish that the demo's scope was accidental.

**Shared runtime:** `keyboard_input.h` supplies physical key identity, Unicode/
UTF-8, modifiers, press/release/repeat and semantic input context. It exposes a
key filter before application/native keypad delivery and optional keypad
interception. The context-scope helper restores the preceding context. The
navigation contract aliases F/X/Z/C outside text mode. Its device implementation
uses xkbcommon and compose; it also supplies a Cardputer-specific default map and
runtime map loading. The default map still has all 32 expected assignments,
including code 92 as slash.

Applications must distinguish native LVGL navigation events from the structured
keyboard event, and must not retain the borrowed event object. Consume decoded
text at that API boundary; sending it through another raw decoder would apply
translation twice. The prepared decoder’s LVGL/special-action values are not interchangeable
with the shared backend's evdev/keysym/semantic fields.

**Build and ownership:** this shared implementation is source integrated through
SCons/Kconfig with dependencies including libinput/xkbcommon/udev. It is not a
header-only replacement for the Template's CMake reader. An installed launcher
does not automatically supply its internal input objects to a separate app.
Migration needs deliberate build, event, lifecycle and dependency integration.

**Keyboard Guide:** useful for diagnosis and understanding image-dependent
modifier reporting. It includes sysfs, legacy I2C and evdev fallback behavior.
That diagnostic role does not make direct modifier-register access necessary
for normal text input. Do not copy its legacy I2C ownership into every app.

## Use, adapt or depart

| Area | Recommendation | Reason and boundary |
|---|---|---|
| Physical symbols and Fn assignments | **Use official** | Complete guidance/map exists. The independently checked fixture matches it; no evidence justifies a competing map. |
| New shared-runtime app | **Use official backend; adapt app callbacks** | Rich decoded input/context/filter APIs already exist. Keep my visual preferences above that boundary. No separate decoder alongside it. |
| Existing Template/CMake apps | **Adapt Template** | The native subset does not satisfy text entry. Retain existing qualified integration while evaluating a focused source extension and its tests. Avoid a broad architecture migration merely to eliminate repeated files. |
| Portable decoder | **Candidate focused extension, not yet a new library** | It isolates raw-event translation for Template consumers and already has three identical copies. Central versioning might reduce maintenance, but it must retain provenance/tests and justify its integration cost. |
| Broader layouts and composition | **Evaluate official xkb path** | The generic profile in the proposal is US-oriented and the symbol loader expects the complete known map. It is not feature-equivalent to xkb composition or arbitrary UTF-8 remapping. |
| Shortcuts, editor focus, Help and menu controls | **Adapt per app** | Official contexts/filtering provide foundations; the app owns whether an action is available, consumed or restored after an overlay. |
| A wholesale alternative keyboard subsystem | **Defer** | This review finds no demonstrated need to replace the shared runtime. No intentional departure is selected at that level. |

This recommendation is conditional on the app's chosen build/runtime, not a rule
that every app must use SCons, a supervisor or a different firmware image.

## Verification and limits

- Compiled and ran four unmodified selected official tests on macOS arm64 with
  ASAN/UBSAN, warnings as errors: input creation/deletion lifecycle, keyboard
  thread lifecycle, keyboard UTF-8/semantic navigation/queue contract, and nested
  input-context restoration. All passed; leak detection was disabled.
- Independently compared the 32 defaults in the current official keymap source
  with the previously captured vendor fixture in Mesh; all code/name pairs match.
- Inspected Template mapping/reader, shared headers, text helpers, delivery/filter
  path, queue, device reader, build selection, relevant tests, guidance and
  diagnostic source. This is a focused evaluation, not a full SDK security audit.
- No complete SDK build/suite, Linux xkb runtime, actual raw-reader-to-editor
  integration or physical keys were newly qualified. Existing app tests and
  installed-device checks do not qualify a future shared component migration.
- The reviewed shared queue push allocates nodes without an explicit cap in that
  function. Do not assume the entire input pipeline is bounded simply because
  it is official; producer/consumer behavior needs evaluation before adopting it.
  This observation is not a demonstrated whole-system failure or an upstream fix.
- No app source, device, source pins for the prepared contribution, firmware or
  publication state was changed. Downloaded sources and test binaries/logs stay
  in ignored build storage; only report/evidence metadata is recorded here.

## Next implementation decision

First document a Template input integration profile: required behaviors, boundary
between decoder and reader, callback/focus ownership, supported versions and tests.
Reuse the existing prepared example where it fits. Compare that profile with a
shared-runtime integration example before deciding whether the personal library
needs a versioned Template extension or only integration guidance and tests.
No extraction or migration is authorized by the existence of this report alone.

[Inventory](library-inventory.md) · [Principles](library-principles.md)
· [Keyboard chapter](05-keyboard.md) · [Guide index](../README.md)
