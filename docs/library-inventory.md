# Personal library: component inventory and proposed first scope

Reviewed 2026-11-18 against local source, under the
[agreed principles](library-principles.md). This inventory proposes what to reuse;
it does not extract components, change applications or select a new framework.

## Source and evidence boundaries

| Alias | Project directory | Reviewed HEAD | Working tree |
|---|---|---|---|
| Mesh | `m5stack-cardputer-zero-mesh-app` | `5f21eebe83402119c5c3ad3a3aee3aef905fccd3` | Clean |
| Surveyor | `m5stack-cardputer-zero-wireless-surveyor` | `a4d1c278d12a87f0ed89f0aaffd6555e768856b5` | Clean |
| NFC | `m5stack-cardputer-zero-nfc-tools` | `8e4c8841e37630f36819598354ed522ebcfe6fcc` | Substantial tracked and untracked changes; provisional evidence |

Paths below are relative to the named project. The
[evidence manifest](library-inventory-evidence.json) records hashes for 53 source,
test and documentation files, including NFC's inspected working-tree additions.
Its HEAD alone does not identify NFC's current implementation. Recheck that work
before extracting anything. Hashing a file is not a complete correctness audit.

Official coverage uses the previously reviewed Template `477fa6d`, launcher/shared
components `4c05b44`, LVGL `85aa60d` and the prepared keyboard proposal recorded in
[component decisions](components.md). No fresh upstream comparison, builds,
hardware operation or test execution against these apps was performed for this
inventory. Referenced tests are coverage to retain and inspect, not newly passed
qualification. App working trees were left untouched.

## Inventory

| Piece and source entry points | Existing reuse and official relationship | Recommended disposition and remaining work |
|---|---|---|
| **Keyboard decoder** — all three: `src/platform/keyboard_decoder.{h,cpp}` | Both files are byte-identical across all three apps. MIT-marked; decoder uses LVGL key constants but owns no LVGL objects or hardware. Official map remains authoritative. Prepared Template integration already exists in the guide. | **First code component.** Package existing decoder, provenance and complete independent map fixture together. Preserve text/navigation context, modifiers, reset and symbol-map validation. Avoid a second map or incompatible decoder beside the official runtime. |
| **Evdev reader and shortcut routing** — all three: `src/platform/linux_input.cpp`, `tests/keyboard.cpp`; NFC also `tests/app_evdev.cpp` | All three reader files differ; tests differ too. Shared concepts include event decoding, text-entry policy and pre-editor routing. App listeners/focus ownership and cleanup are integration concerns. | **Integration adapters and tests for the first component**, not a blind file replacement. Compare APIs and loss/disconnect/repeat/hold cleanup before choosing a common seam. Prove raw events reach an actual textarea and consumed shortcuts do not type. |
| **Home carousel** — Mesh `src/view/screens/menu_screen.cpp`; Surveyor `src/view/screens/survey_screen.cpp`; NFC `src/ui/app.cpp::home` | All use the centered selection, neighboring icons and slide/fade treatment; Surveyor explicitly attributes its adaptation to Mesh. Surveyor/NFC use 180 ms motion. Each owns different navigation and screen state. | **Next UI candidate.** An item-driven presentation component with callbacks; retain each app's navigation authority. Test wraparound, direction, rapid changes, animation destruction and focus on return. Prefer the MIT Mesh source for extraction; NFC's containing file is GPL-marked. |
| **Selectable lists** — Mesh `src/view/widgets/list_selection.h`; Surveyor screen/controller; NFC `App::list` | Shared rounded fill and left accent rail, but Mesh styles existing rows, Surveyor models rows by IDs/kinds/actions, and NFC renders its own list. Similar appearance does not establish the same interface. | **Next UI candidate**, with stable item identity, selected/disabled state, safe clamping and visibility. Keep domain actions outside the widget. Preserve Back focus and test empty, rebuilt and last-item states. |
| **Theme and semantic colors** — Mesh/Surveyor `src/view/theme.{h,cpp}`; NFC `src/ui/theme.h` | Mesh/Surveyor adapt Template palettes and have semantic status colors. NFC uses a smaller palette with amber accents; Surveyor uses burgundy. NFC's palette header is MIT-marked although its enclosing app is GPL. | **First design specification**, then optional small theme data component. Separate accent/selection choices from success/warning/error meanings. Support app palettes rather than imposing one color. Keep contrast and both-theme checks. |
| **Typography, spacing and screen geometry** — Surveyor `src/view/typography.h`, screen layout; Mesh theme/assets; NFC `App::label/list` | Surveyor has explicit 14/12 px body/supporting font helpers. NFC uses 14 px list labels but also 10 px supporting text. Mesh and Surveyor use AssetManager; NFC often uses built-in fonts. All target 320×170. | **Design specification first.** Agree on font sizes, content/footer budgets and fallback behavior. Do not make a font helper pull in the whole AssetManager. Retain line-height/containment checks and long-text cases. |
| **Text editors, forms and confirmation flows** — Mesh message/settings screens; Surveyor screen/controller editor; NFC `App::text/confirm/form` | Repeated edit/save/cancel needs, with different validation, focus and sensitive-operation semantics. Official LVGL textarea and Template input are useful foundations. | **Later UI adapters/patterns.** Keep validation and actions supplied by each app. Preserve drafts on failed saves, consume overlay input and restore focus. Destructive or hardware-specific consent remains domain-owned. |
| **Help, toast and progress** — Mesh/Surveyor `src/view/widgets/{help_popup,toast}.*`; NFC methods inside `App` | Mesh/Surveyor toast implementations differ and reference BaseViewModel/AssetManager; HelpPopup references app page enums. NFC is not using these classes. Timers, observer lifetime, parenting and modal input matter. | **Later focused widgets.** Retain official widget foundations and parameterize content/theme instead of importing app models. Do not turn every startup synchronization event into a toast. Test destruction with timers/overlays active. |
| **App shell, subjects, bindings and assets** — Mesh/Surveyor `src/app`, `src/reactive`, `BaseScreen` | Template-derived foundation already supplies much of this. `subjects.cpp` is identical between Mesh/Surveyor, but `bindings.cpp`, assets and screen managers differ. NFC uses a different single-App organization. | **Reuse official foundation.** Identical inherited plumbing is not by itself a reason to publish another shell. Small integration recipes can expose our preferred carousel/list/theme without importing Mesh pages or creating a competing runtime. |
| **Title/status and screenshots** — Mesh/Surveyor `src/platform/{device_status,screenshot_service}.cpp`, title bars | Source files differ; both depend on app assets/status and rendering context. NFC uses its own UI/render path. Template already has status/screenshot facilities. | **Reuse/adapt official pieces**, documenting one-line headings, explicit source of status, overlay capture and private screenshot destinations. Synthetic preview generation belongs in development tooling, not an always-running service. |
| **Private durable storage** — Mesh `application_config.cpp` and supervisor store; Surveyor SQLite model; NFC `src/core/core.cpp::atomic_write`, `Store` | INI, SQLite and bounded JSON serve different needs. NFC's writer uses a private temp file, fsync, rename and directory sync. Domain schemas, retention and opt-out semantics differ. | **Recipes and acceptance cases first.** Validate candidate data before publishing runtime state, define failure/commit behavior, permissions, migration and deletion. Do not merge three schemas into a universal database layer. |
| **UI/background work boundary** — Mesh SupervisorClient + supervisor; Surveyor Acquisition/controller jobs; NFC Reader/helper | Three distinct choices: persistent radio owner, in-process bounded worker, and short fixed-purpose privileged helper. UI-thread delivery and ownership are shared concerns; lifetime and authority differ. | **Architecture recipes**, with cancellation, result identity/generation, bounded queues and stale-result handling. Mesh's modularity is a supported option, not a required supervisor for every app. No common privileged helper or universal IPC protocol proposed. |
| **Diagnostics and result reporting** — Mesh delivery/health; Surveyor unscored checks; NFC Result/unknown mutations | All need truthful pending/success/failure/unknown states. Surveyor separates validity from failure reasons; NFC distinguishes interrupted mutations from known results. Meaning and recovery stay domain-specific. | **Behavioral contract and examples.** Share safe presentation vocabulary and stale-result rules, while preserving precise reasons and evidence limits. A generic success boolean is insufficient for every operation. |
| **Build/package and regression tooling** — app CMake/packaging/tests; guide offline preflight and prepared contribution verifier | Official Template/CPack/APPLaunch contracts already exist. Apps add exact-source identity, sanitizers, synthetic rendering and data-preserving upgrade checks. Existing scripts have app-specific paths/dependencies. | **Reusable recipes/tooling**, after parameter review. Preserve source/artifact identity, installed-vs-running checks, notices and realistic preservation tests. Keep build, container, device and physical checks distinct. Do not duplicate AppBuilder or invent another installer. |

## Differences to decide together

These are preferences to resolve, not defects established by this inventory:

- **Color:** parameterize burgundy and amber; choose defaults per app.
- **Supporting text:** Surveyor's 12 px helper and NFC's 10 px details differ.
  Choose a baseline using real 320×170 examples before enforcing consistency.
- **Footer content:** Mesh's contextual/action-oriented footer and Surveyor/NFC's
  navigation hints differ. Decide which help belongs in the footer versus Help,
  preserving useful actions and space for content.
- **Selection:** list selection uses a left rail/fill; Mesh message bubbles have
  their own red outline. Treat these as distinct semantic states.
- **Architecture:** background lifetime and hardware authority determine the
  process model. Visual consistency does not require identical backends.

## Proposed version 0.1

This is a candidate scope, conditional on reviewing current official guidance
and implementations first. The inventory's older official source pins are
historical comparison evidence, not completion of that current review.

**Next step:** evaluate the official Template and shared runtime's keyboard/input
guidance, implementations, examples and applicable changes. Compare their
integration paths with our needs and record a use-as-provided, adapt or deliberate-
departure decision, including the possibility that no separate input component
is needed. Only then design the selected integration or extraction.

If justified by that evaluation, the first implementation should be small enough
to adopt and compare safely:

1. **Keyboard/input package:** the identical MIT decoder, official-map provenance,
   independent fixture, and reconciled regression harness. Document the evdev
   integration contract and app-specific adapters; do not assume their current
   reader implementations are interchangeable.
2. **Design reference:** named color roles, app palette variants, type/spacing
   decisions, selection examples and navigation/footer conventions. Resolve the
   open preferences above before treating them as defaults.
3. **Integration example:** a small Template-based editor/list example using the
   existing prepared contribution where suitable, with fake input and no hardware
   acquisition. This can be a development fixture, not another installed app.
4. **Architecture recipes:** Mesh's persistent owner, Surveyor's bounded worker
   and NFC's fixed helper as alternatives, including costs, authority and cleanup.

Carousel and list widgets are the next code candidates after the input component
has a stable interface. They need extraction work; this inventory does not call
them ready-made drop-in components. Avoid including complete app controllers,
radio/NFC operations, privilege rules, storage schemas or network-service adapters
in the initial general package.

## Extraction and acceptance gates

- First evaluate current official guidance and implementation for each candidate;
  record source revisions, fit, limitations and the use/adapt/depart decision.
  Recurrence in our apps alone does not settle that decision.
- Preserve M5Stack and other notices. Inspect file-level licenses and dependencies;
  NFC's GPL-marked UI/core and Mesh's GPL supervisor are not automatically MIT
  because other files or the communication boundary are MIT. Prefer an existing
  appropriately licensed source and review terms before copying or distribution.
- Use immutable source snapshots. NFC's uncommitted work must be stabilized or
  explicitly snapshotted before it becomes a library baseline.
- Retain independent expected input vectors and actual evdev/editor tests; add
  lifecycle/focus/animation tests for extracted UI. Historical app passes alone
  do not qualify a new package or its integrations.
- Adopt one component at a time in an existing app, compare behavior and both-theme
  rendering, then verify another consumer. Keep app-specific behavior and state.
- Document supported LVGL/build/input versions, ownership and update procedure.
  Investigate official changes before maintaining a separate implementation.
- Discuss each meaningful departure and any proposed upstream sharing under the
  [library principles](library-principles.md). No upstream submission is implied.

[Guide index](../README.md) · [Official component decisions](components.md)
