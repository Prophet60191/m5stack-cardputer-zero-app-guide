# 6. Building and packaging

From source to an installed `.deb`. Start a native app from the official
**[CardputerZero/Template](https://github.com/CardputerZero/Template)** (MIT, LVGL 9.5, CMake, C++);
it gives you the MVVM scaffold, the simulator, and the cross-build/packaging presets.

## Develop in the desktop simulator — and why

**Build and run the UI in the desktop simulator first; flash to the device only to confirm.** The
template ships this: a desktop preset builds an SDL window that renders the *real* LVGL UI at the
device's 320×170, using the same screens, widgets, fonts, and theme as the device build.

Why it's the right default:

- **The device loop is slow and fragile.** Cross-compile → package → copy → install → relaunch is
  minutes per change, and the device's Wi-Fi can be flaky. The simulator is seconds, on your laptop,
  no network.
- **It's the same UI code.** LVGL draws identically; only the *frame* differs (an SDL window vs the
  framebuffer). Layout, navigation, theming, and flow are faithful.

What the simulator **can't** do is the real hardware — the radio, the camera, the Cap. Those run
through the **supervisor on the device** (or a mock), never in the UI process (see
[architecture](03-architecture.md)). The UI should be fully usable in the simulator with the
supervisor stubbed.

### Desktop build (example: macOS Apple Silicon)

```bash
brew install cmake ninja libpng jpeg fmt sdl2 freetype dpkg zlib
cmake --preset darwin-arm64                        # fetches LVGL 9.5 on first configure
cmake --build build/darwin-arm64 --config Release
./build/darwin-arm64/Release/<app>                 # opens the SDL window
```

Linux desktop: `sudo apt install -y build-essential cmake ninja-build libpng-dev libjpeg-dev
libfmt-dev libsdl2-dev libfreetype-dev zlib1g-dev`, then the `linux-x86-64` preset. (On Windows, use
the `win32-msvc`/`win32-mingw64` presets; deps come through vcpkg.) Preset families: `linux-x86-64`,
`darwin-arm64`, `darwin-x86-64`, `win32-msvc`, `win32-mingw64`, each with `-dbg`/`-rel`.

> Note: the template's README badge may say "SDL3", but the dependency it actually pins is **SDL2** —
> trust the SDL2 install commands.

## Add a screen (the recipe)

Adding a screen is a few small, local edits — sources are globbed, so a new file is picked up with no
CMake change:

1. **The screen file** — `src/view/screens/<name>_screen.{h,cpp}`, subclassing `BaseScreen`,
   implementing `build_content(lv_obj_t* content)`, calling `init()` in the constructor. Use the
   viewmodel's subjects, the asset manager's fonts, and the theme-binding helpers.
2. **The page id** — add a value to the `AppPage` enum and bump the count.
3. **The viewmodel navigation** — add `show_<name>_page()`.
4. **The screen manager** — add `show_<name>_screen()` and a `case` in its page switch.
5. It's reachable: set the page and the manager reacts (you never load a screen directly from UI
   code). Wire a key/button to `show_<name>_page()` for direct access.

## Cross-build to a device `.deb` (C++)

```bash
cmake --preset cp0-cross                # cross toolchain; may fetch the device BSP/SDK on first run
cmake --build --preset cp0-cross-rel
cpack --preset cp0-cross-deb            # -> dist/<App>_<ver>_rev<n>_arm64.deb
```

- **Toolchain:** `aarch64-linux-gnu-` (`crossbuild-essential-arm64` on Debian; a corresponding
  cross-gcc via Homebrew on macOS).
- **Package on a Debian host.** cpack needs `dpkg`, `dpkg-shlibdeps`, `objdump`, and `readelf` to
  resolve dependencies; other OSes may produce a `.deb` with wrong `Depends`.

The resulting package installs the layout from [how an app lives on the device](02-app-anatomy.md).

### Install on the device

```bash
REMOTE_USER=<user> REMOTE_HOST=<device-ip> ./deploy.sh      # copies the .deb over SSH
# then, on the device:
sudo apt install --no-install-recommends ./<App>_<ver>_rev<n>_arm64.deb
```

For a fast dev loop you can skip packaging entirely: build natively on the device
(`cmake --preset cp0-native …`) and copy the binary into `/usr/share/APPLaunch/bin/`, restarting the
launcher to pick it up. Package into a `.deb` when you're ready to release.

## Packaging a Python app

If your app (or just your supervisor) is Python, the proven recipe is to **vendor everything** —
because the Store installs your `.deb` without running `apt-get update`, so an unexpected dependency
can fail against a stale package list:

1. **Stage the on-device tree.** Put the app and its *full dependency closure* under
   `/usr/lib/<pkg>/site` via `pip install --no-compile --target /usr/lib/<pkg>/site .[extras]`, and
   delete pip's generated `bin/` (its shebangs point at the build venv). Put assets/fonts under
   `/usr/lib/<pkg>/…`. Add the `.desktop`, the icon, a `/usr/bin/<pkg>` CLI wrapper, and
   `/usr/share/doc/<pkg>/` (LICENSE, NOTICE, third-party notices, Debian copyright).
2. **Compile bytecode:** `python -m compileall -q --invalidation-mode unchecked-hash
   /usr/lib/<pkg>/site` (files are read-only in `/usr/lib`; `unchecked-hash` skips the mtime check
   and speeds cold start).
3. **Launch via tiny `/bin/sh` wrappers**, not a package shebang. The wrapper exports
   `PYTHONPATH=/usr/lib/<pkg>/site` and `exec /usr/bin/python3 -s -m <module> "$@"` (`-s` ignores the
   user site-dir; exporting PYTHONPATH means child processes resolve the same vendored packages). The
   APPLaunch wrapper runs the UI module; `/usr/bin/<pkg>` runs the CLI module.
4. **Depend only on `python3`.** Everything else is vendored. Control fields: `Architecture: arm64`,
   `Depends: python3 (>= 3.13), python3 (<< 3.14)`, a fitting `Section`, `Priority: optional`.
5. **Build with `dpkg-deb --root-owner-group -Zxz --build <stagedir> <out>`.** This matters:
   `dpkg-deb --build` on a populated directory emits real directory entries — some hand-rolled
   `ar`+`tar` packagers stream only files, producing a `.deb` with zero directory entries that
   **won't install**. Never hand-build the archive. (`umask 022` for deterministic perms; set
   `SOURCE_DATE_EPOCH` + `--clamp-mtime` if you want byte-for-byte reproducibility.)
6. **Smoke-test the staged tree first:** run `python3 -s -m <module> --help` with `PYTHONPATH` pointed
   at the stage. Cheap, and it catches a broken vendor.

## The `app-builder.json` manifest

This is **Store catalog metadata** (separate from the `.deb` build, which gets the `.desktop`/icon
from `assets/`). Fill in **every** field — the publish validator **auto-rejects** the template's
`TODO` placeholders and a `source_repo` that still points at the template.

- **Top level:** `package_name` (Debian name: `a-z0-9.+-`, starts alphanumeric, ≥2 chars),
  `version`, `app_name` (display title), `description`.
- **`store`:** `summary` (≤80 chars), `description`, `categories` (1–2 from a fixed enum),
  `screenshots` (1–6 × **320×170 PNG**), `icon` (square PNG, 256 recommended), `license` (SPDX id),
  `source_repo` (public URL), `author` (`{github, display_name}`), `share_code` (**4 unique
  alphanumerics** — the code users type to jump to your app), and the **7 permission flags**.
- **The 7 permission flags** — `camera`, `microphone`, `imu`, `network`, `additional_hardware`,
  `background_service`, `external_display`. These are **disclosure metadata** shown on the listing,
  **not** an OS sandbox — actual privilege is still the Debian/group/sudoers model. **Declare them
  honestly:** they're how a user sees what your app touches before installing.

## The `czdev` tool and the Store

`czdev` (Python) scaffolds and publishes; it does **not** build the `.deb` (you build with
cmake/cpack or the Python recipe, then hand it the file):

```bash
./czdev login                 # GitHub device-flow auth
./czdev new my-app            # scaffold from the template (renames project/launcher/icons)
./czdev publish --deb build/my_app_1.0.1_arm64.deb   # validates + opens a publish PR
```

What publishing checks: the `.deb` must contain a `.desktop`, a `store` section with ≥1 screenshot, a
valid package name, and a higher version than what's published; **a bundled systemd service running
as root is rejected**; placeholder/default metadata is rejected. The `.deb` goes to a GitHub Release
and the Store records a **SHA-256** of it (there is no code signature — integrity is the checksum plus
a public source repo). The **first** release of a new app isn't auto-merged: you post a short video of
it running on real hardware and a maintainer merges after watching. Package-name ownership is
first-come by GitHub login.

Publishing to the Store is optional — you can distribute entirely through your own GitHub releases —
but matching these checks is what makes any release trustworthy.

---

Next: if your app drives the LoRa Cap — [radio bring-up](07-radio-bring-up.md). Otherwise skip to
[security and publishing](08-security-and-publishing.md).

## Validate the installed result

A manifest is not the package. Give the CMake project version, runtime About text,
Debian control metadata and store manifest one consistent release version; test
that they agree. Keep inherited internal build-target names separate from public
package/display names. Install the real icon at the exact launcher path, plus
all required supervisor files, licenses, user units and scoped policy helpers.
Generate native library dependencies from the built ELF with `dpkg-shlibdeps`
in a matching distro/architecture environment; hardcoding libfmt/libjpeg package
names can produce a package that builds but cannot install.

Respect the actual minimum CMake version (the template currently needs 3.31),
choose a writable package output directory, and inspect both `dpkg-deb --info`
and `dpkg-deb --contents`. Check maintainer scripts, modes, sudoers with `visudo
-cf`, and units with `systemd-analyze verify`. Test a clean install and cold boot
on the target image. Ensure firewall/setup dependencies exist before any daemon
opens a network listener. A service file with no enable/install path does not
provide reboot persistence. Package installation should not silently start RF.

Keep personal checkout paths out of release binaries as well as source files:
use compiler prefix maps and avoid embedding source asset paths in device builds.
State which checks used mocks, containers, simulator, or real hardware; a prior
review or successful build is not proof that the installed/rebooted app is safe.

Use an app-specific settings directory, binary, launcher entry and asset namespace.
Two apps retaining `template-app` settings paths can accidentally share preferences.
Migrate deliberately, and require explicit re-enabling of hardware auto-start. For
INI saves, use a unique private temporary file per writer, sync before atomic
rename, and sync the directory. Escape or reject line breaks in single-line values;
test concurrent writers and malformed/overflowing numeric preferences.

Test the actual user service, not just `systemd-analyze verify`. In a user unit,
filesystem sandboxing can imply a user namespace that maps host root to nobody;
seccomp restrictions can imply NoNewPrivileges. Both can break an otherwise valid
scoped sudo helper. Inspect the live process's UID map/NoNewPrivs and execute the
real privileged check. Use a consistent privilege design; keep root-owned files
protected by DAC when a fixed sudo check requires host credentials.
