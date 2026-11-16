#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Inspect a developer-built .deb and listing. No network, install or publish actions.

Official policy functions are loaded only after their bytes match the reviewed
lock file. The package is streamed, never extracted; maintainer scripts are text.
Run as an ordinary user, preferably in the documented network-disabled container.
"""
import argparse
from email.parser import Parser
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
import tarfile
import tempfile

LOCK = Path(__file__).with_name("store-policy.lock.json")
MANUAL = [
    "Fresh device dependency installation and missing/incompatible dependency behavior",
    "Launcher behavior, permissions, upgrade/restart, cold boot and uninstall",
    "Hardware operation, RF consent/safety and first-release demonstration video",
    "Security/sensitivity review of code, history, package and screenshots",
    "License compliance and correspondence between source commit and built artifact",
    "Current Store policy, account ownership and approval at actual submission time",
]
LIMIT = 1024 * 1024


def run(*args):
    return subprocess.check_output(args, text=True, stderr=subprocess.PIPE, timeout=30).strip()


def read_json(path):
    if path.stat().st_size > LIMIT:
        raise ValueError(f"JSON exceeds 1 MiB: {path.name}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected JSON object: {path.name}")
    return value


def reviewed_policies(packages):
    lock = read_json(LOCK)
    revision = run("git", "-C", str(packages), "rev-parse", "HEAD")
    if revision != lock["packages_commit"]:
        raise ValueError("Catalog checkout differs from store-policy.lock.json; review policy changes first")
    dirty = run("git", "-c", "core.fsmonitor=false", "-C", str(packages), "status",
                "--porcelain", "--untracked-files=all", "--", "pool/main", "policy")
    if dirty:
        raise ValueError("Catalog metadata/policy has local changes; use the unmodified pinned checkout")
    modules = []
    for rel, expected in lock["sha256"].items():
        source = (packages / rel).read_bytes()
        if hashlib.sha256(source).hexdigest() != expected:
            raise ValueError(f"Reviewed policy hash mismatch: {rel}")
        namespace = {"__name__": "reviewed_store_policy", "__file__": str(packages / rel)}
        exec(compile(source, rel, "exec"), namespace)
        modules.append(namespace)
    return lock, modules[0], modules[1]


def source_asset(app, rel):
    if not isinstance(rel, str) or not rel or Path(rel).is_absolute():
        raise ValueError("Asset paths must be nonempty paths relative to the app")
    path = (app / rel).resolve(strict=True)
    if not path.is_relative_to(app) or not path.is_file():
        raise ValueError("Asset escapes the app directory or is not a file")
    if path.stat().st_size > 8 * LIMIT:
        raise ValueError("Listing asset exceeds the local 8 MiB limit")
    return path


def stage_metadata(app, manifest, catalog, dest, uploader, errors):
    pkg = manifest["package_name"]
    published = catalog / "pool/main" / pkg / "meta.json"
    meta = read_json(published) if published.is_file() else {}
    store = manifest.get("store")
    if not isinstance(store, dict):
        raise ValueError("app-builder.json requires a store object")
    update = dict(store, title=manifest.get("app_name", ""))
    # Match czdev's nonempty-field merge; preserve assigned uuid/code on updates.
    for key, value in update.items():
        if key not in ("icon", "screenshots", "author") and value not in (None, "", [], {}):
            meta[key] = value
    author = dict(meta.get("author") or {})
    if isinstance(store.get("author"), dict):
        author.update({k: v for k, v in store["author"].items() if v})
    if author.get("github") and author["github"].casefold() != uploader.casefold():
        errors.append("Declared author.github differs from --uploader; czdev records the authenticated uploader")
    author["github"] = uploader
    meta["author"] = author
    assets = [(store.get("icon"), "icon")]
    shots = store.get("screenshots", [])
    if not isinstance(shots, list):
        errors.append("store.screenshots must be a list")
        shots = []
    if not shots:
        errors.append("czdev requires at least one source screenshot for a binary submission")
    assets.extend((rel, "screenshot") for rel in shots)
    names = set()
    staged_shots = []
    for rel, kind in assets:
        if not rel:
            continue
        try:
            path = source_asset(app, rel)
            basename = Path(rel).name
            target = basename if kind == "icon" else "screenshots/" + basename
            if target in names:
                raise ValueError("Listing assets collide after czdev reduces them to basenames")
            names.add(target)
            out = dest / target
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes(path.read_bytes())
            if kind == "icon":
                meta["icon"] = target
            else:
                staged_shots.append(target)
        except (OSError, ValueError) as exc:
            errors.append(f"{kind} asset: {exc}")
    if shots:
        meta["screenshots"] = staged_shots
    # Unchanged assets on a metadata-merge update come from the trusted catalog.
    for rel in [meta.get("icon"), *meta.get("screenshots", [])]:
        if not isinstance(rel, str) or not rel:
            continue
        pp = PurePosixPath(rel)
        if pp.is_absolute() or ".." in pp.parts:
            raise ValueError("Invalid published asset path")
        out = dest / rel
        previous = published.parent / rel
        if not out.exists() and previous.is_file():
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes(previous.read_bytes())
    (dest / "meta.json").write_text(json.dumps(meta), encoding="utf-8")


def root_service(text):
    section, user, dynamic = "", None, False
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith(("#", ";")):
            continue
        if line.startswith("["):
            section = line
        elif section == "[Service]" and "=" in line:
            key, value = (s.strip() for s in line.split("=", 1))
            if key == "User":
                user = value
            elif key == "DynamicUser":
                dynamic = value.lower() in ("yes", "true", "1")
    return not dynamic and user in (None, "", "root", "0")


def inspect_tar(deb, option, pkg, policy, errors):
    """Stream metadata/text only, with bounded members and text allocations."""
    proc = subprocess.Popen(["dpkg-deb", option, str(deb)], stdout=subprocess.PIPE,
                            stderr=subprocess.DEVNULL)
    desktop = False
    # Mirrors validate-pr.yml's textual floor; not a shell parser/security audit.
    dangerous = re.compile(r"rm\s+(?:-[a-zA-Z]+\s+)*(?:/(?:\s|$)|/(?:bin|etc|usr|var|home|boot|lib))|"
                           r"(?:curl|wget)[^|]*\|\s*(?:ba)?sh|mkfs|/etc/(?:passwd|shadow|sudoers)|dd\s+[^|]*of=/dev/")
    try:
        with tarfile.open(fileobj=proc.stdout, mode="r|") as archive:
            for count, member in enumerate(archive, 1):
                if count > 100000:
                    raise ValueError("Archive exceeds local 100,000-member limit")
                name = member.name.removeprefix("./").rstrip("/")
                parts = PurePosixPath(name)
                if parts.is_absolute() or ".." in parts.parts:
                    errors.append("Archive contains an absolute or parent-traversing member")
                    continue
                if member.isdir():
                    continue
                if option == "--fsys-tarfile":
                    why = policy["install_path_issue"](name, pkg)
                    if why:
                        errors.append(f"{name}: {why}")
                    if member.mode & 0o6000:
                        errors.append(f"{name}: setuid/setgid bits are forbidden")
                    if member.isdev() or member.isfifo():
                        errors.append(f"{name}: special device/FIFO entry")
                    desktop |= name.startswith("usr/share/APPLaunch/applications/") and name.endswith(".desktop") and member.isfile()
                    is_service = name.endswith(".service") and name.startswith(("lib/systemd/system/", "usr/lib/systemd/system/", "etc/systemd/system/"))
                    needs_text = is_service or name.startswith("usr/lib/udev/rules.d/")
                else:
                    needs_text = name in ("preinst", "postinst", "prerm", "postrm")
                    is_service = False
                if not needs_text or not member.isfile():
                    continue
                if member.size > LIMIT:
                    raise ValueError("Unit/rule/maintainer script exceeds local 1 MiB text limit")
                with archive.extractfile(member) as stream:
                    text = stream.read().decode("utf-8", "replace")
                if is_service and root_service(text):
                    errors.append(f"{name}: system service runs as root")
                if name.startswith("usr/lib/udev/rules.d/") and policy["udev_rule_runs_programs"](text):
                    errors.append(f"{name}: udev executes a program as root")
                if option == "--ctrl-tarfile" and dangerous.search(text):
                    errors.append(f"{name}: dangerous maintainer-script pattern; review against Store policy")
        if proc.wait(timeout=30) != 0:
            raise ValueError("dpkg-deb could not read the archive")
    finally:
        proc.stdout.close()
        if proc.poll() is None:
            proc.kill()
        proc.wait()
    if option == "--fsys-tarfile" and not desktop:
        errors.append("Missing regular usr/share/APPLaunch/applications/*.desktop entry")


def check(app, deb, packages, uploader, source_commit=None, meta_only=False):
    lock, meta_policy, paths = reviewed_policies(packages)
    manifest = read_json(app / "app-builder.json")
    pkg = manifest.get("package_name", "")
    if not isinstance(pkg, str) or not re.fullmatch(r"[a-z0-9][a-z0-9.+-]+", pkg):
        raise ValueError("Invalid manifest package_name")
    if deb.stat().st_size > 2 * 1024**3:
        raise ValueError("Package exceeds the 2 GiB release-asset limit")
    control = Parser().parsestr(run("dpkg-deb", "--field", str(deb)))
    errors, warnings = [], []
    version, arch = control.get("Version", ""), control.get("Architecture", "")
    run("dpkg", "--validate-version", version)
    if control.get("Package") != pkg:
        errors.append("Manifest package_name differs from Debian Package")
    if arch not in ("arm64", "all"):
        errors.append("Debian Architecture must be arm64 or all")
    if not control.get("Maintainer"):
        errors.append("Debian Maintainer is missing")
    upstream = version.split(":")[-1].rsplit("-", 1)[0]
    if manifest.get("version") not in (version, upstream):
        errors.append("Manifest version differs from Debian upstream/full version")
    errors.extend(meta_policy["check_maintainer"](control.get("Maintainer")))
    inspect_tar(deb, "--fsys-tarfile", pkg, paths, errors)
    inspect_tar(deb, "--ctrl-tarfile", pkg, paths, errors)
    pool = packages / "pool/main"
    releases = [read_json(p) for p in sorted((pool / pkg).glob("*.deb.release.json"))]
    latest = None
    for previous in releases:
        if latest is None or subprocess.run(["dpkg", "--compare-versions", previous["version"], "gt", latest["version"]],
                                             check=False, timeout=30).returncode == 0:
            latest = previous
        if not meta_only and subprocess.run(["dpkg", "--compare-versions", version, "gt", previous["version"]],
                                           check=False, timeout=30).returncode != 0:
            errors.append(f"Version must be strictly newer than published {previous['version']}")
    if latest:
        if not latest.get("uploaded_by"):
            warnings.append("Legacy catalog entry has no uploaded_by; Store must resolve ownership")
        elif latest["uploaded_by"].casefold() != uploader.casefold():
            errors.append("Package belongs to a different catalog uploader")
    takedowns = packages / "policy/takedowns.json"
    if takedowns.is_file() and pkg in read_json(takedowns):
        errors.append("Package name is reserved by a Store takedown")
    with tempfile.TemporaryDirectory(prefix="cz-store-preflight-") as temp:
        dest = Path(temp) / pkg
        dest.mkdir()
        stage_metadata(app, manifest, packages, dest, uploader, errors)
        bad, advisory = meta_policy["check_meta"](pkg, dest, str(pool))
        errors.extend(bad)
        warnings.extend(advisory)
    expected_name = f"{pkg}_{version}_{arch}.deb"
    if deb.name not in (expected_name, expected_name.replace("~", ".").replace(":", ".")):
        warnings.append(f"czdev will normalize the upload filename to {expected_name}; verify the submitted manifest uses it")
    if source_commit and not re.fullmatch(r"[0-9a-f]{40}", source_commit):
        raise ValueError("--source-commit must be a full lowercase Git commit hash")
    with deb.open("rb") as stream:
        digest = hashlib.file_digest(stream, "sha256").hexdigest()
    if meta_only and not any(p.get("version") == version and p.get("architecture") == arch
                             and p.get("sha256") == digest for p in releases):
        errors.append("Listing-only check requires an existing published binary with matching version, architecture and SHA-256")
    return {"status": "blocked" if errors else "local-checks-pass", "package": pkg,
            "mode": "listing-only" if meta_only else "binary-update",
            "version": version, "architecture": arch, "sha256": digest,
            "declared_source_commit": source_commit, "catalog_commit": lock["packages_commit"],
            "policy_reviewed_on": lock["reviewed_on"], "errors": sorted(set(errors)),
            "warnings": sorted(set(warnings)), "not_verified": MANUAL}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--app", type=Path, required=True)
    parser.add_argument("--deb", type=Path, required=True)
    parser.add_argument("--packages-dir", type=Path, required=True)
    parser.add_argument("--uploader", required=True, help="Expected GitHub login; never authenticates")
    parser.add_argument("--source-commit")
    parser.add_argument("--meta-only", action="store_true", help="Inspect a listing update using its existing published .deb; still never submits")
    parser.add_argument("--json", action="store_true", help="Write JSON to stdout")
    args = parser.parse_args()
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9-]{0,38}", args.uploader):
        parser.error("--uploader must be a GitHub login")
    try:
        result = check(args.app.resolve(), args.deb.resolve(), args.packages_dir.resolve(),
                       args.uploader, args.source_commit, args.meta_only)
    except (OSError, ValueError, KeyError, TypeError, tarfile.TarError, subprocess.SubprocessError) as exc:
        result = {"status": "check-error", "errors": [str(exc)], "not_verified": MANUAL}
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=True))
    else:
        print("STORE PREFLIGHT:", result["status"])
        for key in ("package", "version", "architecture", "sha256", "catalog_commit", "policy_reviewed_on"):
            if key in result:
                print(f"{key}: {result[key]}")
        for key in ("errors", "warnings", "not_verified"):
            for message in result.get(key, []):
                print(f"{key}: {message}")
    return {"local-checks-pass": 0, "blocked": 1, "check-error": 2}[result["status"]]


if __name__ == "__main__":
    sys.exit(main())
