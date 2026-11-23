# Cardputer Zero app-development guide

This repository contains the public guide and its non-publishing validation tool,
not a device application. Read the
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
backend authority. Discuss any preference that also changes behavior; no new
shell framework, app migration or visual-default selection has been implemented.
Read docs/ui-preferences.md before UI reuse: the owner has locked Mesh's exact
home-carousel appearance and feel, pinned with supporting hashes. Comparison
mockups are illustrative, not the reference. Other UI preferences remain open;
recording a preference does not implement or authorize app-wide restyling.
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
