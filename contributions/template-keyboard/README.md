# Prepared contribution: full keyboard input for the official Template

Status: **prepared for review; not submitted or accepted upstream**. Reviewed
2026-11-16. This is a focused patch to an existing app template, not a new general
library, replacement launcher or change to the installed Mesh application.

## Problem and resulting behavior

At Template revision `477fa6d217b683e3084c361a757f03dc8ca9f753`, the native input
adapter recognizes a small navigation subset. An app adding a textarea cannot
type ordinary text or all official symbols through that path. The broader shared
cp0 SDK already has full keyboard contracts and the correct symbol map.

The [patch](keyboard.patch) integrates the existing MIT decoder/adapter foundation
from the Mesh example with that Template. It adds full built-in text, official
Sym codes, Shift/Fn editing, separate US USB decoding, context-aware shortcuts,
bounded polling, source-owned hold cleanup, rollover, event-loss/disconnect handling and pre-editor routing.
The map is reused from M5Stack; it is not a new layout or a claimed vendor-map fix.

Focused textareas select typing context automatically. Custom editors can provide
and later clear a context query. Printable menu shortcuts belong to the editor
while typing; Help/PrintScreen are consumed before text delivery. Existing toolbar
navigation remains available outside text entry. The default demo is retained.

Owner cleanup is scoped to its source device, including same-key holds from two
keyboards; the native and SDL paths share the explicit release contract.

The proposal replaces post-event `attach_key_router()` registration with
`route_key_input()` inside each input read callback, before LVGL delivers text.
Both native and simulator readers are updated together. Custom/forked readers
need the same deliberate integration; this is not a drop-in binary API update.

`APP_KEYBOARD_EXAMPLE=ON` adds a small editor on the counter page, with Tab/Esc
hints, without saving its text or starting hardware/background services. The
example is disabled by default. Applications remain responsible for their own
focus, navigation and action policies.

## Files, provenance and licensing

- [upstream.json](upstream.json): exact Template/LVGL/map/Mesh revisions, original
  fixture SHA-256 and reviewed patch checksum.
- [keyboard.patch](keyboard.patch): relative-path Git diff, including source,
  optional editor, CTest targets, fixture/provenance and attribution.
- [verify.py](verify.py): explicitly applies/builds/tests the proposal in supplied
  clean pinned checkouts. It does not fetch, install, publish or access hardware.
- [LICENSE](LICENSE): MIT; original copyright notices remain in the patch. No GPL
  radio/supervisor/firewall code is included. Dependencies keep their own licenses.
- [PR-DRAFT.md](PR-DRAFT.md): review-ready description, validation and integration
  limits for a possible upstream contribution; nothing is submitted automatically.

The independent fixture is the unmodified original 32-entry M5Stack keymap, not a
table generated from the decoder. Retain it with the tests and source provenance.

## Reproduce the checks

Use an ordinary user, Git, Python 3, CMake 3.31+, Ninja, a C++17 compiler and the
Template's documented development libraries. Fetch source separately; review the
patch before applying it. These commands neither install packages nor touch a device.

```sh
git clone https://github.com/CardputerZero/Template.git build/official-template
git -C build/official-template checkout --detach 477fa6d217b683e3084c361a757f03dc8ca9f753
git clone https://github.com/lvgl/lvgl.git build/lvgl
git -C build/lvgl checkout --detach 85aa60d18b3d5e5588d7b247abf90198f07c8a63
python3 contributions/template-keyboard/verify.py \
  --template-dir build/official-template --lvgl-dir build/lvgl \
  --build-dir build/keyboard-check --mode desktop --sanitize
```

The verifier refuses changed source revisions, dirty checkouts, modified patch
bytes and nonempty build directories. It deliberately leaves the applied patch
in the supplied Template checkout for review; it never resets someone else's work.
For another run, supply fresh checkouts/output paths or review/clean your own
temporary workspace explicitly. Do not run it in a personal application checkout.

For a matching **native Debian 13 arm64** environment, use `--mode native-arm64`.
The [Dockerfile](Dockerfile) supplies build dependencies. CI runs the container
as the runner's ordinary UID, with network disabled, no capabilities, a read-only
root filesystem and no device mounts. The workspace is writable for patch/build
outputs. No package installation or RF/camera/input operation is performed.

## Acceptance and limits

Tests compare all 32 symbols with the independent fixture, exercise modifier and
per-device state, invalid map rejection, editing controls and semantic Fn actions.
On Linux the actual input reader consumes synthetic pipe records and delivers them
through shortcut filtering and LVGL into the example textarea. Cases include
same-batch focus changes, typed toolbar numbers, browsing shortcuts, rollover,
event loss, disconnect and bounded polling. Direct text insertion alone is not
the acceptance test. Default and optional-example builds are checked separately.

Validation results and remaining review points are recorded in
[VALIDATION.md](VALIDATION.md). Automated replay does not prove physical keys,
firmware one-shot/lock transitions, every kernel revision or all UI interactions.
US USB layout is the supported USB profile; international layouts need a matching
backend. Do not silently apply the built-in Sym map to another keyboard.

## Upstream review

The existing [additional-key contribution](https://github.com/CardputerZero/Template/pull/4)
must be considered before proposing overlapping changes. Review the current
Template/shared-backend direction and offer the smallest useful integration/tests.
This bundle is reviewable locally and in this guide's CI; no maintainer has been
contacted and no upstream PR or Store submission has been created.

[Guide index](../../README.md) · [Component decisions](../../docs/components.md)
