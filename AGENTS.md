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
Keep those choices distinct from universal platform requirements; investigate
official design intent and discuss meaningful departures and keep/share decisions.
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
