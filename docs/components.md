# Official components and contribution decisions

The [2026-11-18 UI/shell evaluation](official-ui-evaluation.md) recommends reusing
the appropriate official page/runtime foundation and adapting its presentation.
Custom palettes, menus and layouts do not require a replacement app-shell SDK.
Preserve ownership, input and backend authority; evaluate behavioral changes
separately from appearance.

The [2026-11-18 keyboard/input evaluation](official-input-evaluation.md) checks
current official sources and supplements the historical comparison below. Use
the official shared input backend when that runtime fits; adapt the Template's
navigation subset for text-entry needs. A general replacement keyboard library
is deferred. Existing prepared contribution pins remain unchanged.

Reviewed **2026-11-16**. Start with the official implementation that fits your
project. This is a source-level comparison, not a security certification or a
promise that two different build systems/components can be exchanged unchanged.

## Reviewed sources

| Project | Reviewed revision | What it supplies |
|---|---|---|
| [Official Template](https://github.com/CardputerZero/Template/tree/477fa6d217b683e3084c361a757f03dc8ca9f753) | `477fa6d217b683e3084c361a757f03dc8ca9f753` | CMake/LVGL app shell, screens/widgets, theme/settings, SDL preview and device packaging |
| [Launcher/shared cp0 components](https://github.com/CardputerZero/launcher/tree/4c05b444cb977cb90e2f33eb4c8261226e370713) | `4c05b444cb977cb90e2f33eb4c8261226e370713` | Runtime runner, platform/input contracts and optional services selected through SCons/Kconfig |
| [AppBuilder](https://github.com/CardputerZero/AppBuilder) | Exact reviewed policy/tool revision in the [Store record](store-readiness.md) | Project creation, build/publication workflows and listing integration |
| [Mesh worked example](https://github.com/Prophet60191/m5stack-cardputer-zero-mesh-app/tree/f1c2c77b9ccb1a26ff366539af7d51f371a3e8af) | `f1c2c77b9ccb1a26ff366539af7d51f371a3e8af` | One C++/LVGL UI/Python radio application, its specific fixes and tests |

## Reuse, adapt or contribute

| Area | What exists | Mesh-specific difference | Decision |
|---|---|---|---|
| App shell and widgets | Template `BaseScreen`, reactive bindings, status/nav widgets, Help and toast | Mesh's title bar/viewmodel know about radio, nodes and unread chats | Reuse the official shell; expose app-specific status fields rather than extracting the Mesh screen tree wholesale |
| Keyboard | Shared cp0 backend has the official symbol map/input contracts; Template's device `map_evdev_key()` only handles a navigation subset | Mesh adds a portable per-device decoder and raw-event-to-editor regressions | Prepare a focused Template integration using the official assignments, preserving navigation, simulator routing and tests |
| Settings/storage | Template theme/config and shared configuration service | Mesh's atomic INI saves and chat-history policies contain domain fields | Teach durable/private saves and opt-out semantics; adopt existing storage where suitable; no general persistence library yet |
| Background work | Shared runtime/process/callback services | Mesh owns a radio daemon, private socket, guardian and transient lifecycle | Pick the simplest architecture; reuse compatible official services and document any missing ownership/security behavior |
| Camera/QR | Official Camera and shared camera service | Mesh needs cancellable capture, secret preview and confirmed channel import | Keep a conditional recipe; inspect backend/image compatibility and qualify actual capture before extracting a camera abstraction |
| Packaging/release | Template CMake/CPack and AppBuilder/czdev | Mesh has matching Debian arm64 CI and exact installed-runtime checks | Preserve the official package contract; offer a reusable verification recipe without creating another installer |
| Store checking | Official policy and publishing tools | This guide's offline preflight deliberately cannot publish | Keep the small separate inspection tool and its pinned policy tests; it is not an alternative Store authority |

## Concrete keyboard gap

At the reviewed Template revision, [the native map](https://github.com/CardputerZero/Template/blob/477fa6d217b683e3084c361a757f03dc8ca9f753/src/platform/linux_input.cpp#L185-L215)
returns only selected navigation/shortcut keys. The shared launcher already has
[all 32 symbol assignments](https://github.com/CardputerZero/launcher/blob/4c05b444cb977cb90e2f33eb4c8261226e370713/ext_components/cp0_lvgl/src/cp0/cp0_keyboard_keymap.c).
The opportunity is reliable integration into this Template, not inventing a new
keyboard layout or alleging the official shared map is wrong.

An existing [Template contribution](https://github.com/CardputerZero/Template/pull/4)
also requests additional keys. Inspect its current state before proposing another
upstream change. My [prepared proposal](../contributions/template-keyboard/README.md)
records its exact base, scope, code provenance, tests and remaining qualification.
It has not been submitted or accepted upstream.

## Evidence and limits

The shared repository contains targeted tests for keyboard/input lifetime, screen
cleanup, configuration failure/rollback, process handling and other services. See
its [runner](https://github.com/CardputerZero/launcher/blob/4c05b444cb977cb90e2f33eb4c8261226e370713/ext_components/cp0_lvgl/tests/run_tests.sh)
and [implementation snapshot](https://github.com/CardputerZero/launcher/blob/4c05b444cb977cb90e2f33eb4c8261226e370713/docs/current-implementation-and-components.md).
Selected source/tests and its build workflow were inspected; the complete upstream
suite and device/image matrix were not rerun for this comparison. Do not equate
the existence of tests, a green build, official ownership or a large test count
with blanket reliability. The Template's navigation demo and the broader shared
SDK are different integration paths.

CMake/SDL and SCons/Kconfig do not automatically share build flags, input event
formats, ownership or callback conventions. Review dependencies and licenses,
match the actual image, and exercise the complete path used by the app. The BSP
cross-build archive is a target sysroot; it is not by itself a ready-made app UI kit.

## When a separate library is justified

My [personal library principles](library-principles.md) allow reusable preferences
and deliberate design choices alongside demonstrated fixes. A component can be
useful without establishing a defect in the official implementation.

Require a recurring need or deliberate shared preference, two unrelated applications
that actually use the same interface, useful independent tests, documented
supported versions, clear licenses and an owner for compatibility/security fixes.
Prefer small source components with explicit versions initially. Avoid introducing
a new system-wide service or mandatory runtime dependency without a measured need.

Current direction: preserve tested reuse and record the personal library's
principles while maintaining the general guide and focused keyboard contribution.
The principles do not create a standalone framework or change an app, launcher
or device. Component extraction remains a separate implementation decision.

[Guide index](../README.md) · [Project sections](projects/README.md)


## Review package and Mesh maintenance

The [M5Stack review package](../submissions/m5stack-2026-11-16/README.md) separates
Template integration from Mesh 0.1.11 maintenance. Both carry bounded-poll and
owner-scoped hold cleanup tests, including unrelated-device teardown. It supplies
exact source/patch hashes, reproduction steps, licenses and qualified evidence,
plus the modular-supervisor rationale. Preparation does not submit a PR or qualify
the Template physically. Current personal-library direction is recorded in the
[agreed principles](library-principles.md).


## Worked-example provenance: Tick & Bell

| Area | Source and scope |
|---|---|
| Device input and display | Official pinned CardputerZero Template and LVGL; preserve the documented keyboard mapping and package/launcher layout. |
| Home carousel | Adapted from the approved Mesh presentation and motion; NFC Tools is the visual source for the position dots. |
| Text-only battery | Reuse the official Template device status reader. The guide pattern changes presentation only: plain text aligned at the right, no glyph. |
| Reusable code | The guide's [position indicator](../examples/ui-patterns/carousel-position/README.md) separates the visual cue from the app's selected index. |
| Demo application | Tick & Bell's clock scheduler, date defaults, five original tones and test flows are independent example work, not APIs supplied by M5Stack or Apple. |

The existing two-version device tutorial still uses Guide Counter; Tick & Bell
is a separate example being tested on a device. The app is not submitted to the
Store, and only its own behavior is qualified by its test records.


| Deliberate departure or addition | Why it exists | Limit |
|---|---|---|
| Right-aligned battery percentage instead of Template's battery glyph plus percentage | Keep the exact percentage visible without spending two slots on the same status. Use the official reader, not guessed levels. | No invented value when the device does not report one. |
| Vertical-only submenu selection rather than sharing carousel left/right shortcuts | The list is arranged vertically and horizontal movement has a different job on editable rows. Printed F/X can serve as a convenience outside editors. | No change to the official key map itself. |
| Mesh carousel with NFC-style position dots instead of copying either app's full home screen | The wider active slot shows position even with wrapping, with a non-color cue. A small independent helper avoids importing an app's state and backend. | One implemented consumer so far; reuse is not a claim of cross-app or per-device testing. |
| A small foreground UI backed by a per-user timer service | Closing the UI should not stop an awake device's timers and alarms. A single scheduler owns persistent state. | No power-off or OS-suspend wake guarantee. This is Tick & Bell-specific, not required for other apps. |

The first-device and troubleshooting walkthroughs explain the learning gaps
at the steps where the guide adds something. See the [short route](start-here.md#follow-the-source-as-you-build)
for the official/adapted/contribution labels.

## Standalone system keys

[Normal-user system-key adapter](../contributions/template-system-keys/README.md)
reuses the official mixer implementation with pinned source hashes. Use only
for standalone Template apps; shared-runtime apps already provide global actions.
See [the alignment audit](keyboard-system-actions.md) for integration and limits.
