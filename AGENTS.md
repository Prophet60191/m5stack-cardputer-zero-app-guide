# Cardputer Zero app-development guide

This repository contains the public guide and its non-publishing validation tool,
not a production device application. The Guide Counter teaching patch in
examples/counter-demo is a self-contained exception to keep the device exercise
reproducible; it is not a shared library, product release, or Store submission. Read the
README and CHANGELOG before editing. Keep claims tied to implementation and
verification evidence; distinguish simulator, container and device checks.

The common foundation covers many kinds of CardputerZero Linux apps. Put
peripheral/transport-specific requirements in docs/projects and detailed Mesh
examples in docs/case-studies. Preserve lessons and existing chapter links;
do not make Python, a supervisor, LoRa or a particular toolkit mandatory for all apps.
Check docs/components.md and docs/library-principles.md before extracting shared
components. The personal library preserves appearance/interaction preferences,
application logic and deliberate architecture as well as verified improvements.
Before designating a reusable piece or designing extraction, inspect current
official guidance/implementation/examples and record reviewed versions and a
use-as-provided, adapt or deliberate-departure decision. Existing duplication
does not by itself justify a separate implementation.
Keep those choices distinct from universal platform requirements; investigate
official design intent and discuss meaningful departures and keep/share decisions.
See docs/library-inventory.md and its evidence manifest for the source inventory
and proposed first scope. NFC evidence is an uncommitted working-tree snapshot;
no extraction or new framework has been implemented by that inventory.
The current keyboard evaluation is docs/official-input-evaluation.md: use the
official shared backend for shared-runtime apps; adapt Template text input as
needed. Defer a standalone keyboard library pending integration-profile work.
Do not apply the raw decoder on top of already decoded shared-runtime events.
For UI, read docs/official-ui-evaluation.md: reuse the selected official shell
and adapt presentation. Preserve lifecycle, focus/input, resource ownership and
backend authority. Discuss any preference that also changes behavior. The full
NFC Tools-style home menu is the reference for the author's apps, not an
official platform rule. Read docs/ui-preferences.md before reusing it. Reuse
its shared header rather than recopying coordinates; verify actual fonts,
geometry, keyboard hints and battery behavior before marking an app migrated.
Mesh submenu-list selection styling is confirmed, with a chevron on highlighted
submenu entries and an NFC-style right-side position bar when content overflows.
See the preference record for conditions and source/render evidence; do not copy
NFC's unconditional bar/chevron behavior as the specified rule. Other row types'
affordances and typography remain open, except ordinary boolean setting rows:
the owner selected right-aligned On/Off text, not switches/checkmarks. Keep `>`
for submenu navigation; consult the preference record for remaining row types.
List navigation preference includes wrapping last-to-first and first-to-last,
keeping selection visible and updating the overflow-only position bar. This is
specified behavior, not a claim of an implemented component or app migration.
Focused proposals live under contributions with pinned sources, licenses,
examples and tests. Their
explicit build verifier is separate from the non-executing Store preflight.
Prepare/review contributions here; submitting an upstream PR requires instruction.
Maintained review reports live under submissions with exact revisions and
allowlisted evidence. Generate bundles only from committed source and successful
matching CI; exclude private device logs, backups and configuration.

Preserve the documentation license and attribution. Use wholly synthetic
examples without personal paths, device identities, passwords or private keys.
Cross-app lessons belong in the relevant chapter; specific test results belong
in the worked example's remediation record. Check local Markdown links after
editing, and do not treat successful compilation as hardware qualification.

Keyboard changes must use the official system/vendor map linked in chapter 5.
Keep the complete upstream fixture and raw-event tests with the reusable decoder;
do not reconstruct symbol assignments from memory or treat direct text insertion
as proof of device keyboard handling.

Store rules must cite a reviewed upstream revision/date. Keep the policy lock and
checklist consistent; review policy diffs before changing pinned hashes. The
preflight must never authenticate, fetch, install, execute package scripts, upload
or create PRs. Test synthetic packages with the pinned official policies before
committing tool changes. Keep local acceptance, hardware/security evidence and
actual Store approval separate. A guide change does not authorize app submission.

The 2026-11-22 preference update also locks direct two-choice rows, selection
menus for more choices and grouped task forms. Read docs/ui-preferences.md for
these newer decisions; earlier pending-choice notes do not override that record.
Mesh owns its 0.1.15 implementation/device evidence; no shared library extraction
or cross-app migration is implied by this guide update.

For future apps, consult chapter 4's editor-state, task recovery and saved-setup
lessons; the messaging recipe's search-language contract; and chapter 6's safe
CLI/running-version/private snapshot verification. The lesson index points to
Mesh 0.1.15 evidence. These are documented lessons, not extracted components or
new device qualification; preserve the official-foundation evaluation rule.

For first-time builders, start with docs/start-here.md and docs/first-app.md,
which build the existing official Template counter at pinned revisions. Keep
this small example separate from release-ready identity/package requirements;
do not imply that it is a new app, an extracted library or device qualification.
The independent-reader check in docs/first-reader-check.md remains pending until
an unfamiliar builder actually reports completing it. Keep beginner reading
routes distinct from the full reference, optional recipes and personal preferences.


Header preference (2026-11-23): omit the battery glyph; useful numeric percentage
may remain. See docs/ui-preferences.md. This is personal presentation guidance,
not a replacement for official status sources or a cross-app migration.


## GPS supplement and current Store review — 2026-11-23

The expanded docs/projects/gps-and-maps.md is the dedicated GPS recipe. Read
its pinned official-source/evidence review before reuse: official GPS already
provides parsing, age states, locking/exclusivity and retry. Add owner/API/cache/
UI diagnosis, measurement time, omitted fields, privacy, safe startup timing and
source/recovery qualification without forking that support. Official preinstalled
root GPS packaging is not a third-party Store exemption. Mesh's probe fix is in
Meshtastic, not an M5Stack GPS-app defect. USB receiver work remains deferred.
Store review now pins packages b6c559a and AppBuilder 042356c; both policy-script
hashes are unchanged. Catalog MESH is occupied by meshtandem. Exact Mesh 0.1.18
preflight is blocked by that code, not a new runtime defect. The app's dated
submission report owns dependency/fresh-image/demo/source-release next steps.
No app/device change, new library, authentication, upload, PR or submission.
