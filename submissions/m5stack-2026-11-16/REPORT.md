# CardputerZero keyboard improvements and modular architecture

Prepared for M5Stack engineering and CardputerZero maintainers | 16 November 2026

Independent community engineering review package | Mesh 0.1.11 | Prepared for review, not submitted

## Executive summary

This package contributes tested keyboard integration and lifecycle improvements
for the CardputerZero Linux application ecosystem. It contains two separate code
reviews: a focused integration into the official CMake Template, and a smaller
maintenance patch for the existing Mesh application. It also explains why Mesh
uses a separate resource-owning supervisor and what that modular design achieves.

The official shared keyboard map was already correct. The Template's reviewed
native input adapter recognizes only a navigation subset; its text-entry integration
is the contribution opportunity. Mesh had previously adopted the full official
map. Its new maintenance fixes bound input work and cancel held actions by owner.
No replacement launcher, mandatory Python service or new general SDK is proposed.

| Review item | Target | Result sought |
|---|---|---|
| Full text-entry integration | Official Template, pinned baseline | Ordinary text, all 32 official symbols, safe shortcut routing and an optional editor example |
| Polling and hold cleanup | Mesh 0.1.11, plus the Template proposal | Bounded input work, retained queued events and cleanup scoped to the device owning the hold |
| Architecture explanation | Mesh application and general guide | Make the modularity purpose, benefits, tradeoffs and compatibility boundaries explicit |

## 1. Scope and exact source

[revisions.json](revisions.json) records the exact baseline/target commits, LVGL
revision, independent fixture hash and both patch checksums. [evidence.json](evidence.json)
records the validation actually performed, its environment and remaining limits.
The generated package adds its source manifest and completed CI snapshot.

The Template proposal applies to official baseline
`477fa6d217b683e3084c361a757f03dc8ca9f753`. Mesh maintenance is reviewed from
`c51a45ee61813bf9685766f9f45c95e6778780a5` to
`f1c2c77b9ccb1a26ff366539af7d51f371a3e8af`. These are distinct patches for distinct
repositories. The scoped Mesh patch contains input code/tests; the complete tagged
0.1.11 application supplies its updated version, packaging and documentation.

The official Template uses CMake/LVGL with an SDL preview; the broader shared cp0
runtime uses a SCons/Kconfig component graph. Those input/build contracts are not
interchangeable automatically. An application using the shared decoded event path
should keep that path and avoid applying another raw-symbol decoder to its output.

## 2. Problems, changes and reproduction

### Full keyboard integration into the Template

At the reviewed baseline, adding an LVGL textarea does not make ordinary letters
and the complete symbol layer available through the Template's native adapter.
The proposal integrates a per-device decoder, the original independent 32-entry
fixture and pre-editor shortcut filtering. Built-in CardputerZero and US USB
profiles remain separate. A focused textarea selects typing context; custom editors
can supply their own context query. Both native and simulator routing are updated.

A concrete acceptance example is Sym+N producing `/`, not `:`. This corrects our
historical application integration, not the vendor's map. While editing, toolbar
digits/letters belong to the text field. Outside editing, browsing shortcuts remain
available. Help consumes typing until dismissed. Unbound semantic Fn actions do
not become invalid text. The optional counter-page editor is disabled by default,
saves no text and starts no hardware service.

### Bounded polling without discarding queued text

A native reader previously drained available input without an explicit budget
across LVGL's `continue_reading` callback chain. A stream of modifiers, repeats or
other ignored records could keep that chain busy. The new reader permits 128 raw
read attempts per device poll chain, counting ignored and interrupted reads too.
It then yields, retaining unread records and pending translations for the next poll.
This is a scoped fairness bound, not a measured global UI-latency guarantee.

Reproduction uses synthetic pipe records rather than kernel input injection. A
burst of 140 modifier records followed by a letter must leave the editor unchanged
on the first poll and deliver the queued letter on the next. Seventy ordinary
press/release pairs must produce 64 characters on the first poll and all 70 after
the second, with no loss or duplication. Existing typing/editing cases also run.

### Owned held-key cleanup

A held action has a source input device. Cleanup now cancels that owner's pending
hold when the native object is deleted, input is lost/disconnected, or the SDL
adapter is destroyed. It pauses the pending timer without synthesizing a short
Escape release/click. Deleting or releasing a different keyboard must not cancel
an active owner's hold, even when both devices used the same key code.

The regression starts a hold, advances a simulated clock past the 700 ms threshold
and counts callbacks. An unrelated release/deletion allows exactly one valid hold;
owner deletion or generic adapter cleanup allows no later stale hold. EOF/lost
input, rollover and ordinary releases remain covered. No physical long-press test
or user-visible hang was claimed as newly reproduced on hardware.

## 3. Why Mesh deliberately uses modularity

Mesh needs a native keyboard-first interface, the mature Meshtastic Python client,
radio reception after the UI closes and explicit ownership of child processes and
shared Cap resources. The design separates those responsibilities behind a small,
documented local protocol. Its purpose is independent development and verification
of presentation, authoritative application state and resource lifetime.

<!-- architecture-diagram -->

| Module | Responsibility and boundary |
|---|---|
| C++/LVGL UI and input | Presents state, handles keyboard/navigation and sends named actions. Holds a read model, not radio authority. |
| Python supervisor/application services | Owns radio/configuration decisions, history/delivery state and validated requests. Uses the existing Meshtastic client. |
| Guardian and user-service lifecycle | Contains descendants, preserves background lifetime and stops/reaps before restoring supported hardware state. |
| Narrow firewall monitor | Provides required enforcement/health evidence through a capability-limited service while UI/supervisor remain ordinary-user processes. |

**Purpose and goals.** Keep the interface responsive, give confirmed state one
owner, make resource cleanup deliberate and permit smaller independent changes.
A keyboard fix can be tested without RF; screen development can use fake state;
radio behavior need not be reimplemented for each view. Reopening the UI can attach
to the existing radio owner rather than restarting reception.

**Benefits supported by the design and tests.** Native input tests exercise the
actual reader with pipes and LVGL. Backend tests use fake radio/sysfs controls with
real pinned protocol/event dependencies. The service/guardian have explicit
ownership and failure-path tests. The deployment verification distinguishes installed
files from running code and checks actual process/permission boundaries. These are
concrete seams for testing and selected reuse, not proof of a completed general SDK.

**Intentional difference from the shared framework.** The official shared runtime
provides native optional services. Mesh chooses a separate Python resource owner
for its particular dependency, background-lifetime and containment needs while
retaining platform launcher/input/package contracts. This is a compatible internal
composition choice, not a claim that other apps or M5Stack should adopt Python.
A calculator or small local utility can remain a single process.

**Costs and limits.** The extra process consumes resources and requires protocol
validation, deadlines, reconnect state, dependency management and coordinated
upgrades. Modularity alone provides no security boundary or automatic cleanup.
The Unix socket is a same-user control API; other programs running as that user
remain trusted to request actions. Loopback clients, local keys/history and root
access remain sensitive. A guardian cannot guarantee restoration through physical
power loss or kernel failure, and software cannot verify an antenna. No quantified
battery-life or memory-saving claim is made for the architecture.

The [architecture decision](https://github.com/Prophet60191/m5stack-cardputer-zero-mesh-app/blob/f1c2c77b9ccb1a26ff366539af7d51f371a3e8af/docs/architecture.md)
and [security model](https://github.com/Prophet60191/m5stack-cardputer-zero-mesh-app/blob/f1c2c77b9ccb1a26ff366539af7d51f371a3e8af/docs/security.md)
provide the detailed interfaces, ownership and limits.

## 4. Validation and what remains unqualified

The package's evidence file separates local tests, exact-source CI, installed
runtime checks and manual hardware qualification. Mesh's backend suite has 98
cases; native sanitizer checks and Debian arm64 build/install/upgrade/firewall
checks accompany the input regressions. Template verification applies the
checksummed proposal to a clean pinned upstream checkout, builds the optional
editor, runs decoder/reader tests and separately builds the ordinary example-disabled app.

Passing automated replay is not a claim that an operator pressed every physical
key or that every image/firmware transition is qualified. The Template proposal's
complete physical key sweep, hold/one-shot/lock transitions and full manual demo
navigation remain separate checks. US USB decoding does not cover international
layouts. Prior Mesh hardware results are not transferred automatically to the
modified Template. Outdoor GPS, public-peer and physical IPv6 gaps are unrelated
and remain explicitly documented. The installed Mesh check does not require
installing the optional Template example or transmitting test RF messages.

## 5. Licensing, sensitivity and requested review

The contributed input/Template files are MIT licensed with original M5Stack and
community attribution. Their original fixture/provenance and full notices travel
with the patch. The Mesh supervisor/helpers retain GPL terms; linked dependencies
and fonts keep their own licenses. A socket boundary is not an automatic licensing
exemption. This package does not copy GPL radio helpers into the MIT contribution.

Only public source, synthetic test inputs and allowlisted evidence are included.
Device identities, personal paths, credentials, private channel material, real
conversations, coordinates, raw device logs and backups are excluded. Public
copyright/GitHub attribution is intentional. The package builder does not install,
transmit, authenticate or submit anything to M5Stack/the Store.

We request engineering review of the keyboard integration and tests, guidance on
fit with the current Template/shared-backend direction and coordination with
[existing additional-key PR #4](https://github.com/CardputerZero/Template/pull/4).
Maintainers can consider the integration, tests or smaller portions independently.
No acceptance, official endorsement or upstream submission is claimed.

## References

- [Official Template baseline](https://github.com/CardputerZero/Template/tree/477fa6d217b683e3084c361a757f03dc8ca9f753)
- [Shared runtime/component contracts](https://github.com/CardputerZero/launcher/blob/4c05b444cb977cb90e2f33eb4c8261226e370713/docs/current-implementation-and-components.md)
- [Official 32-symbol map](https://github.com/CardputerZero/launcher/blob/4c05b444cb977cb90e2f33eb4c8261226e370713/ext_components/cp0_lvgl/src/cp0/cp0_keyboard_keymap.c)
- [Mesh source and tests](https://github.com/Prophet60191/m5stack-cardputer-zero-mesh-app/tree/f1c2c77b9ccb1a26ff366539af7d51f371a3e8af)
- [General guide, optional project recipes and preserved lessons](https://github.com/Prophet60191/m5stack-cardputer-zero-app-guide)
