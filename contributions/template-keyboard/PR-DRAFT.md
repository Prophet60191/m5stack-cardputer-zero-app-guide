# Integrate full CardputerZero keyboard text input with the Template

Adding a textarea to the current Template still leaves ordinary text and most
symbols unrecognized by its native input adapter. This change integrates the
official 32-symbol assignments and a per-device decoder, so Sym+N types `/`,
Shift/Fn editing works, and toolbar digits type into the focused editor.

Route global shortcuts before LVGL text delivery in both the native reader and
desktop virtual keypad. Bound polling and handle rollover, event loss and
disconnect. Limit each poll chain to 128 raw read attempts without discarding
queued text. Scope held-action cleanup to its owning input device, so deleting
that device cancels stale holds while another keyboard's release/deletion does
not. Keep the existing navigation demo; an optional counter-page editor
demonstrates text entry without persistence, radio dependencies or a new service.

Validation: clean-checkout macOS arm64 and Debian 13 arm64 ASAN/UBSAN builds pass.
Portable tests compare the complete independent vendor fixture; Linux tests pass
synthetic raw events through the production reader, shortcut filter and LVGL
example editor. Separate example-disabled app builds also pass. CI repeats the
proposal verification on Ubuntu x86_64 and native Debian arm64.

The patch targets Template `477fa6d217b683e3084c361a757f03dc8ca9f753` and preserves
MIT attribution/provenance. The map already existed correctly in the shared cp0
backend. This is an integration proposal for the CMake Template; applications
using the shared backend should continue to use its event contract.

Review points: `route_key_input()` replaces post-event router attachment; custom
input readers need the same pre-delivery integration. Physical key/firmware modes,
manual complete-demo navigation and image variants still require qualification.
Coordinate with existing additional-key PR #4 before proposing overlapping work.

This is a local draft for review, not a submitted pull request.
