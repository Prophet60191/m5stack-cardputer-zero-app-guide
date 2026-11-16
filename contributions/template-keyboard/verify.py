#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Apply the reviewed proposal to a clean pinned checkout, build and test it.

Unlike the Store preflight, this explicitly compiles/runs source in the supplied
workspace. It never fetches, installs, publishes or accesses device hardware.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess

ROOT = Path(__file__).resolve().parent


def run(*args):
    return subprocess.check_output(args, text=True).strip()


def checked_sources(template, lvgl):
    meta = json.loads((ROOT / "upstream.json").read_text())
    patch = ROOT / "keyboard.patch"
    if hashlib.sha256(patch.read_bytes()).hexdigest() != meta["patch_sha256"]:
        raise ValueError("Patch differs from the reviewed checksum")
    for path, revision in [(template, meta["template_commit"]), (lvgl, meta["lvgl_commit"])]:
        if run("git", "-C", str(path), "rev-parse", "HEAD") != revision:
            raise ValueError("Source checkout differs from the reviewed revision")
        if run("git", "-C", str(path), "status", "--porcelain", "--untracked-files=all"):
            raise ValueError("Use clean source checkouts; no reset/cleanup is performed")
    subprocess.run(["git", "-C", str(template), "apply", "--check",
                    "--whitespace=error-all", str(patch)], check=True)
    return patch, meta


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--template-dir", type=Path, required=True)
    parser.add_argument("--lvgl-dir", type=Path, required=True)
    parser.add_argument("--build-dir", type=Path, required=True)
    parser.add_argument("--mode", choices=["desktop", "native-arm64"], default="desktop")
    parser.add_argument("--sanitize", action="store_true")
    args = parser.parse_args()
    if hasattr(os, "geteuid") and os.geteuid() == 0:
        parser.error("Run as an ordinary user in the documented build environment")
    template, lvgl, build = (p.resolve() for p in (args.template_dir, args.lvgl_dir, args.build_dir))
    if template == lvgl or template in lvgl.parents or lvgl in template.parents:
        parser.error("Provide separate Template and LVGL checkouts")
    # CMake writes its cache/outputs here; keep it outside either source tree.
    if build == template or template in build.parents or build == lvgl or lvgl in build.parents:
        parser.error("Use a separate empty build directory outside the source trees")
    if build.exists() and any(build.iterdir()):
        parser.error("Use a fresh build directory; no existing build is overwritten")
    if args.mode == "native-arm64":
        if platform.system() != "Linux" or platform.machine() not in ("aarch64", "arm64"):
            parser.error("native-arm64 requires the documented Debian 13 arm64 environment")
        release = dict(line.split("=", 1) for line in Path("/etc/os-release").read_text().splitlines() if "=" in line)
        if release.get("ID", "").strip('"') != "debian" or release.get("VERSION_ID", "").strip('"') != "13":
            parser.error("native-arm64 requires Debian 13")
    patch, meta = checked_sources(template, lvgl)
    subprocess.run(["git", "-C", str(template), "apply", "--whitespace=error-all", str(patch)], check=True)
    fixture = template / "tests/fixtures/cardputerzero-keymap.map"
    if hashlib.sha256(fixture.read_bytes()).hexdigest() != meta["fixture_sha256"]:
        raise ValueError("Independent official fixture differs")
    options = ["-DBUILD_TESTING=ON", "-DAPP_KEYBOARD_EXAMPLE=ON", "-DCMAKE_BUILD_TYPE=Debug",
               f"-DFETCHCONTENT_SOURCE_DIR_LVGL={lvgl}"]
    if args.mode == "native-arm64":
        options += ["-DUSE_DESKTOP=OFF", "-DCM0_SDK_ROOT=/", "-DCM0_ALLOW_FETCH_DEPS=OFF"]
    else:
        options += ["-DUSE_DESKTOP=ON"]
    if args.sanitize:
        for name in ("CMAKE_C_FLAGS", "CMAKE_CXX_FLAGS", "CMAKE_EXE_LINKER_FLAGS"):
            options.append(f"-D{name}=-fsanitize=address,undefined")
    subprocess.run(["cmake", "-S", str(template), "-B", str(build), "-G", "Ninja", *options], check=True)
    subprocess.run(["cmake", "--build", str(build), "-j", "2"], check=True)
    env = dict(os.environ)
    if args.sanitize:
        env["ASAN_OPTIONS"] = "detect_leaks=0"  # LVGL process-global allocations.
    subprocess.run(["ctest", "--test-dir", str(build), "--output-on-failure"], env=env, check=True)
    # The optional example must not be required to compile the normal app.
    subprocess.run(["cmake", "-S", str(template), "-B", str(build), "-DAPP_KEYBOARD_EXAMPLE=OFF"], check=True)
    subprocess.run(["cmake", "--build", str(build), "--target", "template_app", "-j", "2"], check=True)
    print("Pinned proposal applied, example/default apps built and regressions passed.")


if __name__ == "__main__":
    main()
