# M5Stack engineering review package

Status: prepared for review, **not sent or submitted**. The report is independent
community work. The earlier physical Template checks/upstream submission remain
deferred; the tested Mesh maintenance update and its documentation are separate.

Start with [REPORT.md](REPORT.md), [revisions.json](revisions.json) and
[evidence.json](evidence.json). The generated PDF is the polished reading copy;
Markdown is maintained as the source. The package contains:

| Item | Purpose |
|---|---|
| Report, revisions and allowlisted evidence | Scope, concrete failures/fixes, exact sources, tests, qualification limits and modularity rationale |
| `template/` | Complete MIT proposal, independent fixture inside its patch, licenses, verification tool, Docker recipe and draft PR description |
| `mesh-input-maintenance.patch` | Only the input/test delta from the documented Mesh baseline; not a complete release/installer upgrade |
| `mesh-source.tar.gz` and Mesh notices | Exact full application source for review, including current version/docs and its distinct component licenses |
| `template-baseline-source.tar.gz` | Exact official Template source baseline, with its original licenses/assets |
| `CI-EVIDENCE.json` | Successful run/source/patch correlation for the completed guide and application checks |
| `MANIFEST.json`, `SOURCE_GUIDE_COMMIT`, `SHA256SUMS` | Source identity, file inventory and integrity checks; no developer signature or Store approval is implied |

## Reproduce the Template review

The source archives permit offline inspection, but contain no Git metadata or
preinstalled build dependencies. For the automated verifier, obtain clean Git
checkouts of the exact Template/LVGL revisions named in `revisions.json`.
In the generated package, `template/README.md` and `template/verify.py` provide
the commands; replace the repository's contribution-directory prefix with
`template/` when working from this bundle. Run as an ordinary user in the documented development
container/environment. The verifier checks source revisions/cleanliness and patch
bytes, applies the proposal, builds/tests and separately builds the normal app.
It deliberately leaves its supplied temporary source checkout patched for review.
No device or package installation is needed.

For repository users, the same proposal lives at
[contributions/template-keyboard](../../contributions/template-keyboard/README.md).
Existing shared-cp0 users should continue using their decoded-event backend;
do not layer another symbol decoder on top of it.

## Reproduce the Mesh maintenance review

Use the exact full Mesh source archive for 0.1.11, or check out the target commit
in `revisions.json`. Follow its `docs/build.md` and `tests/linux-package-check.sh`.
The native/Linux targets are `mesh_keyboard_regressions` and
`mesh_keyboard_evdev_regressions`; they exercise synthetic pipes and LVGL without
opening real input/RF devices. The app's documented Debian container supplies the
matching dependencies for full package/backend checks.

To inspect only the change, apply the scoped patch to the **baseline** Mesh commit
listed in `revisions.json` with `git apply --check` first. That four-file patch omits
the release-version/docs changes by design; use the complete target source or
verified release package for deployment. It must not be applied to the Template.

## Build the PDF and bundle

From a checkout of this guide, use a Python virtual environment with
[requirements.txt](requirements.txt).
The [builder](build_package.py) uses supplied local Git checkouts/evidence; it never
fetches, installs, transmits, authenticates, contacts maintainers or creates PRs.
Generated files stay under `build/` and outside Git.

```sh
python3 submissions/m5stack-2026-11-16/build_package.py \
  --output build/m5stack-review --report-only
```

For a complete submission-ready bundle, additionally pass `--mesh-repo`,
`--template-repo` and `--ci-evidence` pointing to the exact local source checkouts
and completed CI snapshot. See `--help`. The builder refuses mismatched revisions,
patch checksums or unsuccessful/mismatched CI evidence. A checksum verifies bytes,
not trust or correctness. Verify `SHA256SUMS` after extraction.

The report is [CC BY 4.0](../../LICENSE). Template/input code remains MIT; Mesh
source retains its MIT/GPL split and bundled-component notices. Full notices are
included rather than relicensing third-party material. Review remaining physical
checks and existing PR #4 before any upstream submission.
