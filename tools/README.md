# Offline Store preflight

`store_preflight.py` reads a developer-built `.deb`, its source `app-builder.json`
and an explicit pinned official catalog checkout. It **does not** authenticate,
fetch, install, execute package scripts, access hardware, upload or open a PR.
Its only writes are temporary listing assets/JSON, automatically removed afterward.
JSON output goes to stdout; use ordinary shell redirection to retain a report.

Requirements: Python **3.11+**, Git, `dpkg` and `dpkg-deb` (Debian 13 is a suitable
environment). Run as an ordinary user. This is an inspection helper for developer
artifacts, not a hardened malware-analysis sandbox; prefer a network-disabled,
unprivileged container when inspecting unfamiliar packages. Archives are streamed
without extraction, with local limits of 100,000 members, 1 MiB per inspected text
file/JSON and 8 MiB per listing image; overly large inputs fail the check.

## Prepare the reviewed catalog separately

This explicit setup step uses the network. The preflight itself never does:

```bash
git init build/store-packages
git -C build/store-packages fetch --depth=1 https://github.com/CardputerZero/packages.git b6c559a0448aae7715c4b45678a0b89c9eceb12b
git -C build/store-packages checkout --detach FETCH_HEAD
```

[store-policy.lock.json](store-policy.lock.json) records the upstream review date,
exact packages/AppBuilder commits and SHA-256 of the two official policy scripts.
The tool verifies checkout identity and clean catalog metadata, then verifies
policy bytes **before** loading their functions. Policy code is not downloaded or
vendored here. The reviewed functions run in the current process; a verified hash
is a trust decision, not sandboxing. Do not run the tool as root.

Before a real submission, compare current upstream changes with the lock. Review
policy behavior/API changes, update the lock/docs together, fetch that explicit
revision and rerun tests. Never auto-refresh hashes merely to make a check pass.
The pinned catalog makes results reproducible; it cannot prove live availability.

## Run without publishing

From this guide checkout, with the app and `.deb` paths adjusted:

```bash
python3 tools/store_preflight.py \
  --app ../my-app \
  --deb ../my-app/build/my-app_1.0.0-1_arm64.deb \
  --packages-dir build/store-packages \
  --uploader your-github-login \
  --source-commit 0123456789abcdef0123456789abcdef01234567 \
  --json > build/store-preflight.json
```

`--uploader` is the intended account, not authentication. The optional source
commit is recorded as **declared** provenance; the tool does not prove that the
binary was built from it. Verify the build/CI evidence separately. Relative
listing assets must stay inside the app checkout, including symlink resolution.
Local inputs may contain private paths/metadata: review reports before sharing.

For a listing-only update, add **`--meta-only`** and supply the existing published
`.deb`. The tool requires its version/architecture/SHA-256 to match a catalog
record, checks ownership/listing rules and does not require a version increase.
It does not submit anything. Without this flag, a binary update must be strictly
newer than every published version. Both modes retain the manual evidence list.

| Result | Exit | Meaning |
|---|---|---|
| `local-checks-pass` | 0 | Implemented local checks passed against the pinned snapshot; manual evidence and eventual Store approval remain unverified |
| `blocked` | 1 | Concrete metadata/package/catalog blockers listed; fix or resolve the policy conflict before submitting |
| `check-error` | 2 | Invalid/unreadable input, unavailable tool, changed policy/catalog or another incomplete check; never interpret as a pass |

The official metadata policy supplies categories, placeholders, dimensions,
permissions and title/code uniqueness. Its install-path and udev functions are
used directly. Additional inspection checks control/manifest versions, architecture,
Maintainer, archive modes/special entries, default/root system units, installer
patterns, catalog ownership/takedowns and Debian version ordering. Listing fields
are staged using the reviewed `czdev` nonempty-merge/basename conventions.

The small root-service/script checks follow the reviewed PR validator's textual
floor; they are not full shell/systemd parsers. The helper does not reproduce
PR diffs, GitHub authorization, legacy ownership recovery, signatures, complete
launcher semantics or dependency resolution. A filename warning allows `czdev`'s
documented upload normalization; verify the final submitted filename/manifest.
The JSON always lists hardware/security/fresh-install/provenance evidence as
**not verified**. Use the [full checklist](../docs/store-readiness.md).

## Tests and CI

```bash
CZ_STORE_PACKAGES="$PWD/build/store-packages" python3 -m unittest discover -s tests -v
```

Tests construct synthetic `.deb` packages with `dpkg-deb --build` (never install).
They cover all-at-once metadata failures, bad dimensions/permissions, uniqueness,
identity-preserving merges, versions/ownership, root units, paths/setuid/udev,
asset escape, corrupt packages and hash rejection before policy execution. A
sentinel in a maintainer script verifies that inspection never runs it. The
[CI workflow](../.github/workflows/check-guide.yml) uses the exact pinned snapshot.

The tool/tests are [MIT](LICENSE). The guide remains CC BY 4.0; official policy
code remains in its own upstream repository and is not relicensed or copied here.

## Offline reading edition (PDF)

The separate [PDF builder](build_guide_pdf.py) renders the maintained Markdown
as a complete reading edition. It does not call the Store preflight, access a
device, publish or upload. Install Python packages reportlab, markdown-it-py and
pypdf, and supply DejaVu Sans regular/bold/oblique/bold-oblique plus DejaVu Sans
Mono font files and their license notice.

```bash
python3 tools/build_guide_pdf.py --edition 2026-11-18 \
  --font-dir /path/to/dejavu-fonts \
  --font-license /path/to/DejaVu-LICENSE.txt
```

Output defaults to ignored build/guide-pdf/output/pdf. The PDF includes a cover,
linked contents, chapter bookmarks, readable tables/code, page headers/numbers,
an attached Markdown/evidence snapshot and font notices. The manifest records
edition, page/chapter count and SHA256. Review rendered pages before sharing;
text extraction alone does not establish layout quality. This reading edition
preserves pending preferences and historical qualification limits.
