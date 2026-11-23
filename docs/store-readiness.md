# Store readiness checklist

Use this alongside chapters [6](06-building-and-packaging.md) and
[8](08-security-and-publishing.md). Reviewed **2026-11-23** against
[`packages` b6c559a](https://github.com/CardputerZero/packages/tree/b6c559a0448aae7715c4b45678a0b89c9eceb12b)
and [`AppBuilder` 042356c](https://github.com/CardputerZero/AppBuilder/tree/042356c579d728d684eccb68ed9f8669a32822bc),
plus the [official submission guide](https://github.com/CardputerZero/cardputerzero.github.io/blob/5d5123ca05bfc23e5a920f4e9fdbfaf12685e3ab/docs/en/CP0_submit.md).
Check for upstream changes again before publishing; this dated snapshot does not
reserve a code/name or guarantee future Store approval.

## Listing and package

- [ ] Package name, display title, actual binary/runtime version and manifest agree.
- [ ] Unique title (case/whitespace normalized) and four-letter/digit share code
      (case-insensitive); check current catalog and reserved/taken-down names.
- [ ] One or two exact allowed categories; accurate summary/description, prerequisites,
      author, source URL and license. Remove inherited template identities.
- [ ] Exactly seven boolean permission declarations, including supervisor behavior.
- [ ] One to six 320×170 PNG screenshots and a square 128–512 PNG Store icon;
      inspect their actual contents/metadata for sensitive information.
- [ ] Inspect actual `.deb`: architecture, Maintainer, Debian version/revision,
      launcher entry/icon/Exec, package-related paths/names, dependency metadata,
      service identities, modes, udev rules and maintainer-script text.
- [ ] No prohibited root/default-user system services, setuid/setgid files, device
      nodes, unrelated system paths or dangerous installer patterns.
- [ ] Dependency plan records bundled components, Debian dependencies, external
      prerequisites, supported versions/ABI and ongoing updates/license obligations.
- [ ] Run [preflight](../tools/README.md) on the exact release candidate; resolve
      all local blockers and review warnings. Save its JSON privately with evidence.

## Quality, safety and evidence

- [ ] Fresh supported image: dependencies install, app opens from the launcher,
      missing/incompatible prerequisites produce useful recovery instructions.
- [ ] Actual upgrade preserves user settings/data, restarts changed services, and
      verifies live version/PID/privilege state. Test cold boot and uninstall.
- [ ] Applicable keyboard/camera/radio/GPS/network checks have explicit outcomes;
      record simulator/container/replay/physical checks separately and state gaps.
- [ ] Secrets/sensitivity review covers code, history, package, images, logs and
      video. License notices/source obligations reviewed for bundled components.
- [ ] Public source commit/tag, exact artifact SHA-256 and test results recorded.
      Verify downloads again after publication; do not substitute a rebuild.
- [ ] Synthetic hardware-demo content prepared; no account tokens, messages,
      real coordinates, private channel QR/URL or unnecessary device identifiers.

## Submission and later updates

1. **Review first.** The checklist/preflight does not log in or submit. Resolve
   open policy questions and select the concrete artifact/listing/video first.
2. **Choose a submission route and authenticate only for publishing.** The official
   [Developer Center](https://dev.cardputer.cc/) also accepts a `.deb`, parses its
   metadata and creates the submission PR after the contributor confirms upload.
   It and the CLI share server-side policy; neither is a way around review.
   For the CLI, `czdev login` uses GitHub device flow and
   stores credentials locally. Protect those credentials and use the intended
   account: the recorded uploader controls the package name. It is not based on
   matching the Debian Maintainer's email.
3. **Publish deliberately.** `czdev publish --deb <exact-file>` uploads the binary
   to a release in the contributor's packages fork and opens a metadata/manifest PR
   against `CardputerZero/packages`. This is a write operation. There is no
   `publish --dry-run` in the reviewed CLI. On acceptance, the official pipeline
   promotes the binary and regenerates the catalog/index.
4. **First submission.** Post a short video of the app running on a real
   CardputerZero in the PR comments; a maintainer reviews/merges it. Passing CI
   does not auto-merge a new package name. Track PR approval, promotion/index job
   success and the final listing/download independently.
5. **Binary updates.** The current catalog retains the highest Debian version
   per app; promotion can supersede older manifests and later clean their official
   binary assets. Do not promise users a permanent Store rollback archive; keep
   a separate verified release/rollback plan.
   Use the recorded owning account and a strictly higher
   **Debian** version. The reviewed policy allows validated updates to merge
   automatically; versioning is not determined by the GitHub release title/tag.
   `1.0.0~rc1-1` sorts before `1.0.0-1`; marking a GitHub release “prerelease”
   does not change an embedded Debian `Version: 1.0.0-1`. Decide version policy
   before a candidate is submitted and never replace an accepted version's bytes.
6. **Listing-only updates.** `czdev publish --meta-only` updates an existing
   listing without a new binary/version, subject to ownership and metadata checks.
   Retain assigned identity (`uuid`, existing share code) and verify staged assets.

References: [schema/review rules](https://github.com/CardputerZero/AppBuilder/blob/042356c579d728d684eccb68ed9f8669a32822bc/docs/APP_BUILDER_JSON.md),
[publishing implementation](https://github.com/CardputerZero/AppBuilder/blob/042356c579d728d684eccb68ed9f8669a32822bc/scripts/czdev/publish.py),
[validation](https://github.com/CardputerZero/packages/blob/b6c559a0448aae7715c4b45678a0b89c9eceb12b/.github/workflows/validate-pr.yml),
[first-release/automatic-update merge gate](https://github.com/CardputerZero/packages/blob/b6c559a0448aae7715c4b45678a0b89c9eceb12b/.github/workflows/validate-pr-comment.yml).

## Worked example: correcting an overconfident submission report

The supplied Mesh submission report was checked against source and the real
0.1.8 CI artifact, rather than accepted as proof of readiness. These corrections
are useful for any app:

| Report item | Verified disposition and lesson |
|---|---|
| Empty share code / categories `Communication`, `Utilities` | Real manifest blockers; use an available code and exact enum values. Availability is not a reservation |
| “Only two items remain; the package already satisfies the gate” | Incorrect. Local preflight also rejects the 100×100 Store icon, `/usr/bin/mesh-launch` name, and `/usr/lib/systemd/user/cardputerzero-mesh-supervisor.service` path |
| Non-root firewall account and a user supervisor mean the package passes | These address service identity; path and other policies still apply. Resolve the legitimate user-unit path conflict without weakening security |
| A `debian-arm64.yml` workflow builds every package | Mesh actually uses the `debian-arm64` job in `.github/workflows/regressions.yml`; link the real workflow and its successful run |
| Example uses 0.1.7 | Current reviewed candidate is 0.1.8, Debian `0.1.8-rev1`; use metadata from the selected artifact, not copied version examples |
| Separate installation of meshtasticd/Python dependencies is always correct | This is Mesh's chosen plan. Other apps may use Debian dependencies or maintained private bundles; fresh-image install/runtime checks remain required |
| `docs/` does not ship | Mesh installs Markdown/images under `/usr/share/doc/cardputerzero-mesh/docs`, excluding generated PDFs; inspect install rules/archive, not assumptions |

Evidence: [Mesh source fab958d](https://github.com/Prophet60191/m5stack-cardputer-zero-mesh-app/tree/fab958d1add0d9a46cbf7a880faaa4ec005c5283),
package SHA-256 `8ff56073d45b43ed1cd1212f46bbdfcc9e345219c0897fbdf97d5fac2ad7b3b4`;
historical policy/catalog revision `94eb8d7` reviewed on 2026-11-16. A filename-normalization warning
also notes that `czdev` uploads `cardputerzero-mesh_0.1.8-rev1_arm64.deb` based on
the control fields. Missing localization is advisory. No Store submission was
performed in this guide pass, and these blockers are not described as repaired
in the installed app. This record is a dated example, not current app status.


## Current-review boundaries

Both official policy-script hashes are unchanged from the previous lock; the
catalog, CLI and publishing lifecycle have advanced. The lock/CI checkout is
updated only after comparing those sources. Run the exact candidate against
this current catalog: a previously available title/code can become occupied.
On this snapshot `MESH` belongs to `meshtandem`; an older Mesh preflight pass is
not a reservation. See the application's dated submission-readiness report.

Official preinstalled apps and third-party Store packages can have different
privilege policies. The official GPS example's root/sudo packaging is not a
third-party exemption from the Store's no-root rule. Reuse its appropriate
parser/model ideas while preserving least privilege in the package being submitted.
