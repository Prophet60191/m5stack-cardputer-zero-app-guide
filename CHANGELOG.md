# Changelog

## 2026-11-26 — Worked upgrade and rollback

- Add a Tick & Bell walkthrough for preserving a saved alarm, verifying the running scheduler, and rolling back.
- Rehearse both package transitions and backup recovery in disposable Debian arm64.

## 2026-11-26 — First-app showcase and shell scope

- Connect the guide, working Tick & Bell example and reusable App Shell.
- Define a fresh-checkout path from a first screen edit to an installable package.

## 2026-11-26 — App Shell simulator workflow

- Document which edits update in place, which need a deliberate reopen, and how to start fresh.
- Add the macOS-verified walkthrough for preserving an active field, unsaved text and cursor.

## 2026-11-26 — Complete reusable NFC Tools-style home menu

- Standardize the home header, typography, icon lanes, dots and keyboard footer; show real battery percentage at right.
- Document the carousel explicitly as a personal preference and teaching example.

## 2026-11-26 — Tick & Bell and online publishing

- Add Tick & Bell source links and current simulator screenshots.
- Add reusable NFC-style home-menu geometry and icon sizes.
- Rebuild the online guide from the repository on pushes to main.

## 2026-11-26 — Carousel position indicator

- Add a reusable home-carousel position row based on NFC Tools, with the same vertical title and dot positions.
- Record Up/Down list selection and a right-aligned, text-only battery percentage.

## 2026-11-26 — Guide Counter device exercise

- Add an optional two-screen, separately named counter based on the official
  Template, with a reproducible patch and two installable teaching versions.
- Walk through device installation, first launch, persistent count, upgrade,
  rollback and removal, and add symptom-first device troubleshooting.
- Record desktop event-path and Debian arm64 package checks separately from
  physical-device and independent-reader checks.

## 2026-11-26 — First counter walkthrough

- Put an annotated desktop counter screenshot next to the README quickstart.
- Add a small reset exercise after the greeting edit, with simulator checks
  for the new action and the original controls.
- Keep the independent-builder check pending until a new reader tries it.

## 2026-11-17 — Forms as review and contextual action lanes

- Document complete forms with persistent Save actions, named scan/import success,
  service-side validation without duplicate review pages and specific consent.
- Cover shortcut ownership during typing, held/repeated activation, truthful
  outcomes and Help-based navigation. Preserve invalid-action blocking.
- Preserve safe, fixed diagnostic failure categories and distinguish later
  recovery from evidence identifying or fixing an earlier fault.

## 2026-11-17 — Unified setup and cancellation ownership

- Add local draft/shared-scope/review guidance, stable small-screen headings/help,
  masked secrets, offline versus live verification and explicit partial outcomes.
- Cover cancellation reservations before a worker creates its preview, and preserve
  imported data during unrelated field edits. Keep device-specific qualification
  in the app's implementation record.

## 2026-11-17 — Confirmed local state and measured UI maintenance

- Document correlated acceptance for debounced/idempotent local saves, RAM-only
  versus durable state, bounded retries and graceful shutdown without replaying
  external actions.
- Add stable selection/disappearance, in-place values/highlights, independent
  mode/time freshness and object-bound clock callback guidance. Include cache
  lifetime and unused-style/unused-polling checks when simplifying code.
- Keep host measurements, matching arm64 checks and real device qualification
  distinct. Mesh-specific results stay in its maintenance record.

## 2026-11-16 — Quiet preference synchronization

- Keep startup/reconnect preference synchronization silent without skipping its
  effect; retain useful confirmation for deliberate user changes and visible
  failures. Use correlated acknowledgments and cover enforcement and reconnects.

## 2026-11-15

- Corrected the claim that process exit restores hardware automatically.
- Added lessons on parent-death guardians, advisory ownership locks, persistent
  verified firewall rules, private-channel validation, confirmed privacy state,
  partial-write recovery, bounded work/allocations, authoritative history and
  request/target correlation.
- Added full bundled-component license notices and corrected GPL distribution wording.
- Added app settings namespace, deliberate migration and durable/private INI save lessons.
- Added artifact-level packaging/dependency validation and screenshot/history
  sensitivity checks; distinguished regression evidence from hardware proof.


### Device qualification lessons

- Added dependency-service autostart checks, user-unit namespace/NoNewPrivileges
  interactions, and persisted-profile/schema checks before firmware can broadcast
  or discard stale data in favor of factory defaults.
- Recorded that a reachable control endpoint is required to interpret a blocked
  port test; distinguish real LAN probes from isolated network-namespace tests.


### Public/private policy distinction

- Distinguished a personal private-only setup from a general app's supported
  channel types; public use needs explicit routing and separate location consent.
- Added consent identity/readback, pre-start location-default handling, unnamed
  imports and shared frequency-slot lessons.

### Application follow-up lessons

- Added stable configuration identity and archived-context routing, durable history
  without replay, acknowledgment-source checks and recoverable multi-file changes.
- Added receive-only first-run setup, GPS age, debounced drafts and quiet-hour semantics.
- Added native arm64 CI package artifacts and a capability-owned health monitor
  instead of repeated elevated subprocess checks with unsafe timeout cleanup.
- Added whitelist diagnostics and sensitivity/deletion rules for new durable state.
- Added actual empty-profile startup, explicit protobuf defaults, semantic channel
  capacity/readback, real pubsub contracts and remote-RF receive accounting.
- Added draft-only conversation reachability, receiver versus location consent,
  measured camera deadlines and runner-owned CI artifact staging.

## 2026-11-16

- Added persistence re-enable semantics and an immediate-restart regression for
  existing RAM drafts, with preference changes propagated to all clients.
- Added fixed routing context versus keyboard-help layout, pixel-bound checks,
  grouped settings and display-order-independent action keys.
- Added uninstall cleanup for generated services/shared file-capability grants,
  private data backups and preservation of other apps' dependencies/configuration.
- Added explicit keyboard start/busy/result states for camera operations, repeated
  key suppression, correlated replies, cache reset and honest Escape/disconnect
  behavior for operations that may already have changed state.
- Added selection-border clipping and stable border/padding inset lessons, with
  light/dark rendering checks for tightly fitted LVGL containers.
- Added cancellable capture versus confirmed import, connection/state-bound
  preview tokens, generic request deadlines and queue-independent local storage.
- Added metadata-complete history opt-out, obsolete-grant removal, canonical
  version metadata and greeting dependency/snapshot checks.
- Added post-upgrade service restart, live version/socket peer PID checks and
  the distinction between installed-file hashes and running code.
- Added measured synthetic maintenance workloads, unchanged-state redraw/write
  suppression, typed conversation preparation, stable selection and strict
  validation before Python equality shortcuts.


### Verified keyboard mapping and reuse

- Replaced the incorrect 14-entry symbol table and the false claim that no public
  mapping exists with the complete official 32-entry map and authoritative links.
- Added reusable decoder/fixture/test references; covered built-in versus USB
  profiles, driver-selected symbols, per-device state, semantic Fn actions,
  shortcut consumption, same-batch focus, rollover, event loss and disconnect.
- Require raw-event-to-editor regressions in addition to direct UI tests; keep
  automated replay separate from physical device qualification.


### Store readiness and non-publishing preflight

- Complete the listing contract: exact category enum, title/code uniqueness,
  icon/screenshot dimensions, placeholders, seven permissions and metadata merging.
- Document current install-path, naming, installer-script, service, udev and mode
  rules, including user-unit/sudoers policy gaps; distinguish built-in mechanisms
  from accepted third-party packaging and keep privilege design intact.
- Replace blanket Python-vendoring advice with explicit Debian, private-bundle
  and external-prerequisite plans, including fresh-image/compatibility/update checks.
- Add a release checklist covering account ownership, first hardware video,
  Debian version ordering, binary versus metadata-only updates and promotion.
- Add an offline, non-publishing inspection tool with hash-verified pinned official
  policies/catalog and separate unverified hardware/security/provenance evidence.
  It never authenticates, fetches, installs, executes package scripts or submits.
- Add synthetic package regressions and documentation/policy-pin checks in CI.
  Record every supplied-report correction and actual Mesh 0.1.8 submission blocker;
  no app/device/submission change is included in this guide pass.

Validation: all 14 synthetic-package/documentation tests pass in a read-only,
network-disabled Debian 13 container as an ordinary user. The actual 0.1.8
candidate produces the documented blockers, not a false ready/pass result.


### Store-compatible user-service integration

- Reviewed the catalog advance from 3ed6a23 to 94eb8d7: only a published app's
  metadata/assets/version changed; both policy-script hashes are unchanged.
  Refreshed the pinned catalog snapshot and added the transient user-service
  alternative, including fixed arguments, lifecycle serialization, cgroup/stop
  recovery and actual-device property checks. No Store submission is automated.
- Record the actual-device transient ExecStopPost specifier difference and the
  explicit UID-based runtime-path correction; probe stop/crash/restart recovery
  rather than assuming static-unit command behavior carries over.

## 2026-11-16 — General app guide and focused Template contribution

- Reorganize the reading path into a common CardputerZero Linux foundation,
  architecture choices, optional project sections and worked examples. A local
  utility no longer inherits mandatory Python, supervisor, socket or radio machinery.
- Add utilities, persistence/messaging, GPS/maps, camera/QR, hardware/NFC,
  networking and audio/media recipes, with explicit acceptance and evidence limits.
  Keep LoRa chapter 7 optional. Improve accessibility and scope conditional checks.
- Preserve all 30 moved Mesh lesson blocks in a pinned case study, with a lesson
  index, earlier revision link and existing chapter paths/entry-point aliases.
  Keep actual application/device evidence distinct from new recipes.
- Record a pinned official/Mesh component comparison. Reuse official foundations;
  defer an independent framework until recurring gaps, unrelated consumers and a
  maintenance plan justify one. Official keyboard assignments were already correct.
- Prepare an MIT-licensed keyboard integration patch against the exact official
  Template: portable decoder, per-device state, pre-editor shortcut routing,
  optional counter-page textarea, bounded polling and independent raw-event tests.
  Carry original fixture/provenance and licenses; no GPL radio code is extracted.
- Add a checksum/revision/clean-source verifier and separate desktop/arm64 CI.
  The verifier explicitly compiles/runs source; the non-executing Store preflight
  and its reviewed policy pins remain unchanged. No upstream PR/Store submission
  is created and no Mesh app/device configuration is changed.

Validation: 18 guide/preflight/proposal-guard tests pass in the isolated ordinary-user
Debian container; all recursive Markdown links/anchors pass. Clean-checkout patch
verification passes locally on macOS arm64 and Debian 13 arm64 with ASAN/UBSAN,
including the actual Linux reader into the example textarea, plus separate normal
Template builds with the example disabled. Physical keys and the complete device/UI
matrix remain explicit qualification work; GitHub CI checks the exact pushed source.

### Mesh input maintenance and M5Stack review package

- Carry the Mesh 0.1.11 polling/cleanup maintenance into the prepared Template
  proposal: bound each read chain to 128 attempts, retain queued text and cancel
  held actions only for their owning input device. Add flood/resumption and
  multi-device cleanup regressions; preserve all official symbol fixtures.
- Document Mesh's deliberate supervisor composition, authoritative state,
  background lifetime, testing/reuse goals, costs and same-user trust limits.
  The common guide still permits simple single-process applications.
- Add a separate engineering report, exact revision/patch metadata, allowlisted
  installed-runtime evidence and a reproducible PDF/offline review-bundle builder.
  Include source archives, licenses, draft PR and checksums; require successful
  source-matched application/guide/report CI before final bundle generation.
- Add report-rendering CI and four package-evidence guards. All 22 guide/tool
  tests and clean-source macOS/arm64 proposal checks pass locally. Mesh 0.1.11
  passes exact-source CI and installed-device replay/runtime/preservation checks.
  Physical Template qualification and actual upstream/Store submission remain
  deferred; no test transmission or independent general SDK is introduced.

## 2026-11-16 — Wireless Surveyor cross-app feedback

- Corrected the remaining universal-supervisor wording in the simulator chapter; a foreground app can use bounded workers and supported OS services.
- Added tested worker-construction ordering, transaction-before-dedup and read-only report snapshot lessons; linked observation freshness/units and shared discovery ownership to the primary APIs.
- Recorded the tested local-user-manager versus SSH scan-authorization distinction without prescribing new grants. Added actual endpoint/association attribution and isolated loopback/D-Bus test guidance. These are cross-app lessons; Surveyor-specific results remain in that app. No upstream contact, public repository, Store submission or device policy change.

- Artifact follow-up: documented the tested FetchContent EXCLUDE_FROM_ALL integration after Surveyor's real archive/preflight exposed shared LVGL development payloads. The corrected installer excludes them and keeps its notices.

## 2026-11-18 — Personal reusable-library principles

- Record the agreed principles in docs/library-principles.md: complement official
  firmware/components/guides; preserve my choices for appearance,
  interaction, logic and backend design; investigate intentional differences before claiming defects.
- Use Mesh modularity as an example of a deliberate choice with benefits and
  costs, applied according to each app's needs. Distinguish personal preferences,
  useful alternatives and demonstrated improvements; discuss keep/share decisions
  case by case, including whether to contribute to official developers.
- Link the principles from the guide, component decisions and agent context.
  Clarify that recurring preferences can justify reuse without an official defect.
  Documentation only; no component extraction, application/device change or
  upstream submission. Relative documentation links checked.

## 2026-11-18 — Reusable component inventory

- Inspect source entry points across Mesh, Surveyor and NFC Tools; record the
  component inventory, proposed 0.1 scope and hashes of 53 relevant files.
  Both decoder files are byte-identical across all three apps; evdev adapters,
  tests and other integration code differ. NFC has substantial uncommitted work,
  so its evidence is provisional and does not describe its HEAD alone.
- Separate first input/design candidates, later carousel/list widgets, official
  shell reuse, optional backend/storage recipes and app-specific code. Record
  footer/type/color preferences, file-license boundaries and acceptance gates.
- Link the inventory from principles, README and agent context. App source and
  device state remain unchanged; no build, app test, extraction, deployment or
  upstream submission. Existing guide documentation checks pass.

## 2026-11-18 — Official evaluation precedes reusable-component design

- Make the owner's required order explicit in library principles, agent context
  and inventory: review current official guidance/implementation/examples first,
  then decide use as provided, adapt or deliberately depart, with reasons and
  tradeoffs. Apply this to UI, logic and backend choices alike.
- Mark the initial scope as conditional. The next task is official keyboard/input
  evaluation, including whether a separate component is needed at all; older
  source pins and repeated app code do not complete that evaluation.
- Documentation only; official review/extraction has not been performed by this
  clarification. Existing documentation checks pass.

## 2026-11-18 — Current official keyboard/input evaluation

- Check current official key guidance, Template, launcher/shared input, Keyboard
  Guide and AppBuilder sources; record exact revisions and file hashes. Template
  is unchanged at 477fa6d; reviewed launcher head is 13d2f26. Template PR4 remains
  open/unmerged. Prepared contribution/policy pins remain unchanged.
- Recommend official decoded input for shared-runtime consumers and focused
  Template adaptation for text-entry apps. Defer a standalone keyboard library;
  integration profiles should establish whether code extraction is useful.
- Four selected unmodified official macOS arm64 tests pass with ASAN/UBSAN;
  32 default map assignments match the independent vendor fixture. Full SDK,
  Linux xkb/reader integration and physical keys remain unqualified in this pass.
- Update keyboard guidance to avoid prescribing my decoder for every LVGL app;
  link the decision from inventory, components and agent context. No app/device
  changes, implementation extraction, firmware update or upstream submission.
  Existing guide documentation checks pass.

## 2026-11-18 — Official UI/shell evaluation and preference boundaries

- Inspect current official Template, shared page/runner, HelloWorld, APPLaunch
  carousel/settings and key/UI guidance. Record exact revisions and 108 collected
  reference-file hashes; distinguish collected evidence from a complete audit.
- Decide to reuse the selected official foundation and adapt presentation, with
  lifecycle/input/resource/backend boundaries preserved. Defer a replacement shell.
  Record custom page/bar support, existing widgets, launcher-local dependencies,
  footer recommendations and the behavioral effects to evaluate separately.
- Four unmodified official lifecycle/helper contract tests pass with ASAN/UBSAN
  on macOS arm64. These do not qualify rendered screens or device behavior.
  Link the report from principles/inventory/UI guidance and agent context.
- No app/device changes, visual-default enforcement, extraction, migration or
  upstream submission. Next is the owner's style specification and representative
  states. Existing guide documentation checks pass.

## 2026-11-18 — Home-carousel preference locked

- Record the owner's explicit choice of Mesh's exact home-carousel look and
  feel in docs/ui-preferences.md, with immutable source reference and hashes.
  Preserve its geometry, fonts, theme treatment, wrapping and directional
  slide/fade; comparison mockups do not replace the actual implementation.
- Leave other components open. No app changes, extraction or new device/render
  qualification; documentation checks pass.

## 2026-11-18 — Submenu selection base confirmed; additions pending

- Record the owner's confirmation of Mesh's rounded selected row, palette fill
  and colored left stripe, with the source helper and hash as reference.
- Owner mentioned additional component items; their details/location remain
  pending. Do not infer or finalize them, row content or other behavior.
  Documentation only; no app/device changes. Documentation checks pass.

## 2026-11-18 — Submenu chevrons and overflow-bar preferences

- Record the owner's additional rules: highlighted submenu entries show a right
  chevron; overflowing content has a slim right-side position bar.
- Found the referenced NFC Settings bar in its existing amber render and list
  source. Record both hashes and distinguish the requested conditions from NFC's
  current unconditional nonempty-list bar and all-row chevrons. No app fix or
  device inspection performed; other row affordances/type choices remain open.
- Documentation checks pass; preferences only, no implementation changes.

## 2026-11-18 — Wrap-around list navigation specified

- Reinforce overflow-only visibility for the right-side position bar. Record
  last-to-first Down and first-to-last Up navigation, selection-following scroll
  and marker updates, with empty/single-item and changing-content considerations.
- This is the list-component specification in the preference walkthrough;
  no component/app implementation or device change is claimed. Documentation
  checks pass.

## 2026-11-18 — On/Off row presentation locked

- Record the owner's choice of a setting name on the left and On/Off text on
  the right, instead of switches/checkmarks. Reserve chevrons for submenu
  navigation. Choice selectors, immediate actions and toggle confirmation/state
  handling are not silently settled by this presentation choice.
- Preferences/documentation only; no app/device changes. Documentation checks pass.

## 2026-11-18 — Offline PDF reading editions

- Add a maintained PDF builder and usage instructions for the complete app guide,
  including project recipes, component evaluations and recorded UI preferences.
- Produce a dated 92-page reading edition with linked contents, bookmarks,
  readable tables/code, source/evidence attachments and font attribution.
- Rebuild the current Mesh user manual (40 pages) and upload both PDFs to the
  owner's requested Drive folder; verify uploaded MIME type, size and parent.
- Review every rendered page and check text margins and internal destinations;
  documentation tests pass. No app/device changes or new hardware qualification.

## 2026-11-22 — Everyday interaction preferences and lessons

- Record direct two-choice rows, submenus for more choices, task-grouped forms,
  readable result/value text and Cancel-first irreversible deletion. Keep these
  personal preferences distinct from platform rules and app qualification.
- Add general task clarity/recovery guidance without changing the official
  foundation or creating another shell. Mesh implementation evidence remains
  in that app; no guide-side device qualification is claimed.

## 2026-11-22 — Reading-edition refresh closeout

- Render and review the complete 92-page development reading edition and the
  companion 40-page Mesh manual plus one-page quick reference. Local source/link
  checks pass; generated PDFs remain outside Git and device installers.
- Refresh the owner's existing Drive manuals in place and verify PDF type, size
  and unchanged parent placement. Preserve links and sharing organization.
- Shorten a repeated UI explanation to avoid an isolated end-page line; preserve
  the lesson and cross-reference. Keep implementation qualification in Mesh's
  own refinement record. No official branding or new framework is introduced.

## 2026-11-22 — Reusable findings from the installed Mesh refinement

- Expand UI guidance for explicit editor theme states, meaningful value contrast,
  saved-setup scope, stable destructive targets and nonselectable form headings.
- Add search-language limits and whole-task checks; distinguish host rendering,
  synthetic device replay and physical/hardware qualification.
- Strengthen existing upgrade guidance with safe CLI probes, coordinated service
  restart and logical private data comparisons; avoid duplicate generic chapters.
- Index the lessons and link exact Mesh 0.1.15 source/qualification evidence.
  Radio-specific policy remains an optional example, not a universal requirement.
- Rebuild the 94-page PDF, check links/body bounds and inspect new/reflowed pages
  against the previously reviewed edition. Refresh the existing Drive copy in
  place. Documentation checks pass; no app or device changes.

## 2026-11-22 — Beginner route and first worked build

- Add a short first-app route, capability selector and a pinned official counter
  walkthrough from source to desktop build, greeting edit and arm64 package
  inspection. Reuse the official shell/input rather than create another framework.
- Add an independent-reader exercise; keep its pending status distinct from
  maintainer build checks and physical hardware qualification.
- Reduce repeated form/recovery prose using primary-section links, preserve
  chapter paths/headings and the detailed case studies, and correct simulator
  equivalence/ad hoc install wording. Relevant progress/status is conditional.
- Include the new chapters in the reading edition and replace a stale PDF note
  about an undecided UI choice with a pointer to the authoritative preference record.
- Validate native macOS arm64 build/startup and the greeting edit; clean-build
  and inspect its Debian 13 arm64 package without networking or device installation.
  Record exact sources, artifact hash and remaining checks in the example evidence.
- Pass all 22 guide/preflight tests in Debian; rebuild the 102-page PDF, verify
  the embedded sources and inspect new/reflowed pages. Keep short command blocks
  together and avoid isolated paragraph lines in the reading edition.
- Refresh the existing Drive PDF in place and verify its type, byte count and
  unchanged folder. No app, launcher, radio or device settings were changed.


## 2026-11-23 — Header battery preference

- Remove battery from the generic status example; do not recommend a battery
  icon in app headers. Record the owner's no-icon preference while allowing
  useful numeric percentage and preserving official shell/backend boundaries.
- Mesh 0.1.18 owns implementation and qualification; no other app is migrated.

- Native Mesh checking also caught a partial-framebuffer redraw problem after
  removing a status element. Add the reusable sibling-visibility/hardware check
  and bounded-redraw lesson; desktop rendering alone did not reveal it.


## 2026-11-23 — GPS integration supplement and refreshed submission guidance

- Expand the existing GPS chapter into a dedicated official-first integration
  recipe; preserve the official parser/age/locking/retry work and identify added
  cache/owner/UI diagnosis, source timestamps, privacy and timing/side-effect
  lessons. Pin reviewed official GPS/site/source hashes; correct stale Mesh
  outdoor-pending wording while retaining exact qualification limits.
- Review current development/submission/CLI/catalog sources. Refresh dated policy
  lock/CI catalog pins after confirming both policy scripts unchanged; document
  the Developer Center route and current version-retention lifecycle.
- Exact Mesh 0.1.18 package checked in an offline container against the current
  catalog is blocked because MESH belongs to meshtandem; record this in the app's
  separate readiness report. No app metadata/runtime/device or submission change.
- All 22 guide/preflight tests pass against the refreshed catalog. Rebuild and
  visually verify the reading edition before refreshing its existing Drive copy.

- The final reading edition is 105 pages (655020 bytes); GPS, Store and case-
  study reflows are visually reviewed. Preserve the existing Drive ID/folder.

## 2026-11-23 — Cover attribution and distribution lessons

- Add the maintainer's public GitHub URL to the PDF cover without a real name.
- Record optional app-private runtime/dependency distribution, official Store APT
  behavior, offline first-launch and cache integrity, safe live-service upgrades,
  paired corresponding source and honest fresh-container/device boundaries.
- Mesh's local minimal Debian 13 container passed offline first launch, reuse,
  cache repair, tamper rejection, QR imports and data-preserving removal. These
  are packaging lessons, not universal architecture requirements or fresh-image
  physical acceptance. No spare card: that hardware test is explicitly deferred.
- All 22 guide/preflight tests pass. The updated 105-page reading edition has a
  visually checked cover/link and packaging section; existing Drive PDF replaced
  in place. Mesh's 42-page candidate manual and one-page reference also refreshed.

- Final packaging review adds `preinst` interpreter Pre-Depends and separate
  manual/installer checksum asset names, preventing dependency-order and release
  attachment collisions. Rebuild and inspect the updated reading edition.


## 2026-11-23 — Complete operational documentation follow-through

- Update the Mesh case study's current dependency plan to 0.1.19 private bundles
  while preserving dated evidence/examples and optional architecture choices.
- Correct the Store example table's old separate-prerequisite statement. Add the
  reusable requirement to document install through rollback/removal, generate
  offline instructions from one runbook, and preserve binary/document provenance.
- Refresh/review the reading PDF with its existing public GitHub cover link and
  maintain its original Drive identity. No app/runtime/device changes here.

- Validation: all 22 guide/preflight tests pass; the 106-page reading edition is
  rebuilt and changed/reflowed pages inspected. The public GitHub cover link is
  preserved. The Mesh operational manual remains 42 pages plus a one-page
  reference; update its current Drive/Desktop and draft copies separately.
