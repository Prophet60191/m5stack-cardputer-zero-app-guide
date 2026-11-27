<h1 align="center">Building Apps for the M5Stack Cardputer Zero</h1>

**[Read the online guide](https://prophet60191.github.io/m5stack-cardputer-zero-app-guide/)**

An independent guide for building many kinds of applications on the **CardputerZero
Linux handheld**: utilities, notes, games, networking tools, media and peripheral
apps. Start with official foundations, choose only the facilities your app needs,
and preserve useful lessons from real projects.

<a id="why-this-exists"></a>
<a id="who-its-for"></a>
<a id="how-to-use-it"></a>

## Scope and starting point

This guide targets the CardputerZero's Debian arm64/APPLaunch environment. The
original ESP32 Cardputer and Cardputer ADV need different firmware, input and
packaging instructions. Hardware/image variants can differ; document your tested
profile and probe capabilities instead of assuming every device has a camera or Cap.

No radio, Python backend, local socket or background service is required by the
guide. C++/LVGL with the official Template is the main native UI recipe. Other
languages/toolkits can follow the same launcher, keyboard, privacy and package
contracts with their own rendering/build implementations.

## Featured example: Tick & Bell

Tick & Bell is the guide's worked app example: a timer and alarm with the
reusable NFC Tools-style home menu. The screenshot below shows that menu in
the desktop simulator.

![Tick & Bell home screen with the Alarms menu selected, shaded side icons, position dots, battery percentage and keyboard hints](docs/images/tick-bell-carousel-position.png)

**[Read the Tick & Bell case study](docs/case-studies/tick-bell.md)** ·
[Browse the app source](https://github.com/Prophet60191/m5stack-cardputer-zero-tick-bell)

<a id="contents"></a>

## Start here

New to this device? Use the [short reading route](docs/start-here.md). The
guide explains the choices, [Tick & Bell](docs/case-studies/tick-bell.md)
shows them in a working timer and alarm, and the [App Shell chapter](docs/app-shell.md)
shows how to start your own app with a small set of reusable components.
[Get the App Shell source on GitHub](https://github.com/Prophet60191/m5stack-cardputer-zero-app-shell).

Want a smaller exercise before starting your own app? The
[simulator counter](docs/first-app.md) runs without a Cardputer Zero. The
[optional device exercise](docs/first-device-app.md) covers installation,
upgrading and rollback with a separate teaching counter. For an existing app
with real state to preserve, follow the [Tick & Bell upgrade walkthrough](docs/upgrade-existing-app.md).

If a build runs on your desktop but not on the device, start with
[symptom-first troubleshooting](docs/device-app-troubleshooting.md).

Returning with a specific task? Use the [project selector](docs/projects/README.md).
Use the chapters below as a reference. Library decisions and historical Mesh
lessons are separate resources further down this page.

## Common foundation

| Read | Covers |
|---|---|
| [1. Platform](docs/01-platform.md) | Device constraints, Debian, launcher and Store |
| [2. App anatomy](docs/02-app-anatomy.md) | Package layout, launcher entry, privileges and resource ownership |
| [3. Architecture choices](docs/03-architecture.md) | A single process, workers or a separate resource-owning service |
| [4. UI and polish](docs/04-ui-and-polish.md) | Navigation, accessibility, overlays, settings, progress and performance |
| [5. Keyboard](docs/05-keyboard.md) | Official map, text/navigation context, modifiers and event-path tests |
| [6. Building and packaging](docs/06-building-and-packaging.md) | Native/Python paths, dependencies, arm64 builds and installed checks |
| [8. Security, licensing and publishing](docs/08-security-and-publishing.md) | Threat boundaries, private data, attribution and release evidence |

For deeper background, read 1, 2 and 3. Then choose the UI/build path and
[project sections](docs/projects/README.md) that apply. Chapter numbers and paths
are retained for existing links; [7. LoRa bring-up](docs/07-radio-bring-up.md) is optional.

## Optional project sections

The [project selector](docs/projects/README.md) covers local utilities, persistent
text/messaging, [GPS/maps](docs/projects/gps-and-maps.md), camera/QR, NFC/other hardware, networked apps and audio/media.
Each section distinguishes transferable patterns, actual examples and qualification
still required for a new app. A radio antenna rule does not become a calculator
requirement; a camera example does not certify every image's camera stack.

## Official foundations and focused contributions

Use the [component comparison](docs/components.md) to see what the official
Template, launcher/shared SDK and AppBuilder already provide, where my Mesh code
is specific to that app, and which gaps are worth addressing upstream.

The first [prepared keyboard contribution](contributions/template-keyboard/README.md)
adds the official symbol map, full text input, an optional editor example and
raw-event/editor tests to a pinned official Template. It is a reviewable proposal,
not an accepted upstream release or a new general framework.

## Personal reusable library

The [UI preference record](docs/ui-preferences.md) tracks my design decisions:
the NFC Tools home menu and the separate Mesh list-selection base are confirmed. Submenu chevrons and overflow indicators are specified.

The [shared NFC Tools-style home menu](examples/ui-patterns/carousel-position/README.md) is my preferred layout and a demonstration, not a platform requirement. See the [Tick & Bell case study](docs/case-studies/tick-bell.md) or [browse the app source](https://github.com/Prophet60191/m5stack-cardputer-zero-tick-bell).

The [carousel position indicator](examples/ui-patterns/carousel-position/README.md) is the first small LVGL component for the shared home-menu pattern.

My [library principles](docs/library-principles.md) record the preferences and
design choices I want to reuse across my apps, including appearance,
interaction, application logic and backend organization. They complement official
foundations and distinguish personal choices, useful alternatives and demonstrated
improvements. I review each meaningful departure before deciding what to keep
or share. These choices remain separate from the general guide's platform requirements.

The [source inventory and proposed version 0.1 scope](docs/library-inventory.md)
compare Mesh, Surveyor and NFC Tools, with file hashes, extraction candidates,
open preferences and licensing/qualification boundaries.
The [official keyboard/input evaluation](docs/official-input-evaluation.md)
records the first use/adapt decision: official shared input for that runtime,
with a focused Template extension considered separately.
The [official UI/shell evaluation](docs/official-ui-evaluation.md) records the
next decision: reuse official foundations and adapt presentation to my preferences,
preserving lifecycle, input and backend ownership.

<a id="the-worked-example"></a>

## M5Stack engineering review package

The [prepared report and review package](submissions/m5stack-2026-11-16/README.md)
explain the improvements, exact sources, tests, licenses and remaining checks,
including Mesh's deliberate modular UI/supervisor design. The package is prepared
for review; no upstream PR, Store submission or new general library is implied.

## Worked examples and preserved learning

The [first counter walkthrough](docs/first-app.md) is the small starting example.
The [independent-reader check](docs/first-reader-check.md) records how to test the
guide without the original chat context; that check is still pending.

Mesh contributed many lessons, but it is one application. The
[Mesh case study](docs/case-studies/mesh.md) retains detailed state, privacy,
conversation, camera and licensing examples with pinned implementation/evidence.
The [lesson index](docs/lesson-index.md) explains where those lessons now live.
The earlier guide remains available through its linked Git revision.

Keep [source-level tests](docs/components.md#evidence-and-limits), container checks,
actual-device qualification and Store admission separate. No test count guarantees
security, hardware compatibility or approval for a different application.

<a id="contributing"></a>

## Release and contribution checks

Use the [Store readiness checklist](docs/store-readiness.md) and
[offline preflight tool](tools/README.md) to inspect a listing and its actual installer
without authentication, upload or submission. Official policy/catalog revisions are
pinned and reviewed; a passing local report is not a Store acceptance.

Corrections, focused examples and tested improvements are welcome. Prefer reusing
or contributing to official components. Consider a separate library only after
recurring needs or shared preferences, two unrelated consumers and a
maintenance/compatibility plan justify it.

## Offline reading edition

The [PDF builder](tools/README.md#offline-reading-edition-pdf) creates a styled
reading edition with contents, bookmarks, internal chapter links and an attached
source snapshot. It includes the current library principles and UI preferences;
generated PDFs stay in ignored build output, separate from device installers.

## License

The guide is [CC BY 4.0](LICENSE), with attribution. The runnable preflight tool
and tests are [MIT](tools/LICENSE). The prepared contribution has its own
[MIT license and notices](contributions/template-keyboard/LICENSE); preserve
upstream attribution and each component's actual terms when reusing code.

Meshtastic is a trademark of Meshtastic LLC; M5Stack and Cardputer are trademarks
of their owners. This is an independent community guide, not an official SDK.

## Maintaining this repository

The root README owns reader navigation. docs/ contains maintained chapters,
recipes, preferences and dated case studies; examples/ contains teaching code;
contributions/ contains focused upstream proposals; submissions/ contains pinned
review reports. [AGENTS](AGENTS.md) governs changes and [CHANGELOG](CHANGELOG.md)
records sessions. [Website maintenance](website/README.md) explains publication;
[tool instructions](tools/README.md) describe offline Store preflight. Generated
build/PDF/site output is not a second maintained copy of the guide. Local edits
are not published until the appropriate source/release workflow completes.
