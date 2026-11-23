# 6. Building and packaging

The C++/LVGL recipes below apply to the official CMake Template. Other stacks
can use the same package/launcher/Store contract with their own build system.
Python dependency plans are a separate path. A backend or service is optional.

From source to an installed `.deb`. Start a native app from the official
**[CardputerZero/Template](https://github.com/CardputerZero/Template)** (MIT, LVGL 9.5, CMake, C++);
it gives you the MVVM scaffold, the simulator, and the cross-build/packaging presets.

## Develop in the desktop simulator — and why

**Build and run the UI in the desktop simulator first; qualify the installed app on the device separately.** The
template ships this: a desktop preset builds an SDL window that renders the *real* LVGL UI at the
device's 320×170, using the same screens, widgets, fonts, and theme as the device build.

Why it's the right default:

- **The device loop is slow and fragile.** Cross-compile → package → copy → install → relaunch is
  minutes per change, and the device's Wi-Fi can be flaky. The simulator is seconds, on your laptop,
  no network.
- **It uses the same UI code.** Preview layout, themes and flow without the hardware.
  Display/input backends, installed fonts and runtime conditions still need device checks.

The simulator does not qualify actual radios, cameras or Caps. Put slow hardware
work behind a bounded worker, a compatible OS service or a resource-owning
supervisor as the app requires (see [architecture](03-architecture.md)). A single
foreground process can use supported OS services without a new daemon. Use fake
source adapters for the simulator and test the real source contract separately.

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

For native device compilation, the official `cp0-native` preset is available,
but keep build dependencies out of a release installer. Prefer a traceable package
install for qualification; an ad hoc binary copy does not verify package paths,
upgrade behavior or the exact artifact users will receive.

## Packaging a Python app

Choose and document a dependency plan before packaging. The Store installs against
the device's available package lists; do not assume it refreshes them or installs
an arbitrary Python environment for you. Three plans are possible:

| Plan | When it fits | What you must verify |
|---|---|---|
| Debian `Depends` | Libraries available for the supported device image | A fresh target image can resolve the actual version/architecture from its configured repositories |
| App-private vendoring | Dependencies you can legally redistribute and maintain | Full dependency closure, native ABI compatibility, licenses/source obligations and a security-update process |
| Explicit external prerequisite | A separately managed daemon, hardware stack or environment | Exact supported versions, installation instructions, runtime detection and a useful missing/incompatible-dependency screen |

Combinations are normal. Mesh currently uses Debian dependencies for native/system
components and separately installed `meshtasticd` plus a pinned app-private Python
environment. That is a distribution choice, not a Store requirement or a GPL
prohibition on bundling. See the [worked example's installation instructions](https://github.com/Prophet60191/m5stack-cardputer-zero-mesh-app#install--run)
and [licensing](08-security-and-publishing.md#licensing-including-the-mitgpl-split).

Test the chosen plan on a fresh supported image, then test missing/incompatible
dependencies, an upgrade, a cold boot and uninstall. Dependency installation must
not silently enable another daemon or start RF; inspect dependency autostart too.
Record what is bundled, what `Depends` resolves and what the user installs. Never
hide a network installer or `pip install` in a root maintainer script.

For the **app-private vendoring** plan, this is a useful recipe:

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
4. **Declare the remaining system requirements.** If the closure is entirely pure
   Python, the runtime dependency may be just `python3`. Native extensions can
   still need shared libraries: derive/check those dependencies too. A Python 3.13
   environment may need `Depends: python3 (>= 3.13), python3 (<< 3.14)`; match the
   tested interpreter/ABI instead of copying that range to every app. Use a fitting
   `Section`, `Priority: optional`, and the correct `Architecture` (`arm64` or `all`).
5. **Build with `dpkg-deb --root-owner-group -Zxz --build <stagedir> <out>`.** This matters:
   `dpkg-deb --build` on a populated directory emits real directory entries — some hand-rolled
   `ar`+`tar` packagers stream only files, producing a `.deb` with zero directory entries that
   **won't install**. Never hand-build the archive. (`umask 022` for deterministic perms; set
   `SOURCE_DATE_EPOCH` + `--clamp-mtime` if you want byte-for-byte reproducibility.)
6. **Smoke-test the staged tree first:** run `python3 -s -m <module> --help` with `PYTHONPATH` pointed
   at the stage. Cheap, and it catches a broken vendor.

## The `app-builder.json` manifest

The top-level fields identify the app/build; `store` supplies the catalog listing.
Keep package, runtime, manifest and release versions aligned. The launcher icon
inside the `.deb` and the Store icon may use separate files; validate both.
The official online build also expects its packaging fields, including `bin_name`;
an app with its own CMake/CI build must satisfy that build's contract separately.
`czdev publish` takes an already-built installer and does not replace its contents.

| Field | Acceptance rule |
|---|---|
| `package_name` | Debian name, at least two characters, lowercase `a-z0-9.+-`, starts alphanumeric; match the `.deb` Package field |
| `version` | Match the built upstream/full version; record a Debian revision separately and use Debian version comparison for updates |
| `app_name` | Store title; unique after case folding and whitespace normalization |
| `store.summary` | Nonempty, at most 80 characters, no template placeholder |
| `store.categories` | One or two exact category names from the list below |
| `store.screenshots` | One to six real PNGs, each exactly 320×170; source paths relative to the app directory |
| `store.icon` | Square PNG, 128–512 pixels per side; 256 recommended |
| `store.license` | Accurate SPDX identifier/expression for what is distributed; the validator checks text, not legal compliance |
| `store.author` | Non-placeholder `display_name`; `github` should match the publishing account |
| `store.share_code` | Exactly four ASCII letters/digits, unique case-insensitively across the catalog; not a placeholder such as TEMP/TODO |
| `store.permissions` | Exactly the seven keys below, each a JSON boolean |
| `store.description`, `source_repo`, `locales` | Recommended by upstream policy; this guide additionally expects public source, clear prerequisites and accurate descriptions |

Allowed categories: `System Tools`, `Development`, `Hardware & IoT`, `Security`,
`Radio & Comms`, `AI`, `Creative & Office`, `Media`, `Games`, `Emulators`,
`Education`, `Lifestyle`, `Other`. Labels such as `Communication` and `Utilities`
are not accepted synonyms.

The seven permission keys are `camera`, `microphone`, `imu`, `network`,
`additional_hardware`, `background_service`, `external_display`. They disclose
capabilities to the user; they do not create an OS sandbox. Declare actual behavior,
including a background process or networking needed by a supervisor.

`czdev` stages icons by basename and screenshots under `screenshots/<basename>`;
avoid basename collisions. It records the authenticated GitHub uploader and merges
nonempty listing updates into published metadata, preserving assigned identity
such as `uuid` and an existing share code. Check code/title availability against
the catalog immediately before submission; a local check cannot reserve either.
Replace template authors, summaries, Maintainer and source URLs before release.

Policy references, reviewed 2026-11-16: [official schema](https://github.com/CardputerZero/AppBuilder/blob/18996b694ae305306fc5d457d982cfba0b0e7cc5/docs/APP_BUILDER_JSON.md),
[metadata validator](https://github.com/CardputerZero/packages/blob/3ed6a232372bdc769826d93aba03fb9b6bbd9589/.github/scripts/store_meta_policy.py).
The [preflight lock](../tools/store-policy.lock.json) records exact revisions/hashes.

## Package layout and installer acceptance

Inspect the actual `.deb`. The current Store checks more than non-root services:

| Area | Required check |
|---|---|
| Identity | Valid Package/Version/Maintainer, supported `arm64` or `all`, no template identity; uploaded filename agrees with control metadata |
| Launcher | Entry at `/usr/share/APPLaunch/applications/*.desktop`; verify its Name/Exec/Icon and graphical `Terminal=false` on the device |
| Executables | `/usr/bin/<name>` must relate to the package name; an unrelated short helper name can fail |
| Data/config | Use package-related directories under `/usr/share`, `/usr/lib`, `/opt`, `/var/lib`; package-related configuration under `/etc` |
| Shared directories | Use the policy's explicit exceptions for APPLaunch, documentation, named completion/man/tmpfiles/udev files and system units |
| Forbidden locations | No `/usr/local`; no merged-usr alias paths such as `/bin` or `/sbin`; no unrelated shared-system filenames |
| Services/privilege | System unit names must relate to the package; no default/root `User`; `DynamicUser=yes` is recognized. No setuid/setgid files or device nodes |
| udev | No `RUN`, `PROGRAM` or `IMPORT{program}` commands that execute as root |
| Maintainer scripts | Read every script without executing it; the Store rejects dangerous textual patterns such as destructive deletion, disk writes, account/sudoers edits and downloaded shell pipelines |
| Size | Release asset limit is 2 GiB; this is not a sensible target size for the handheld |

The authoritative [install-path policy](https://github.com/CardputerZero/packages/blob/3ed6a232372bdc769826d93aba03fb9b6bbd9589/.github/scripts/install_path_policy.py)
and [PR validator](https://github.com/CardputerZero/packages/blob/3ed6a232372bdc769826d93aba03fb9b6bbd9589/.github/workflows/validate-pr.yml)
define the exact floor. The reviewed path policy has an exception for **system**
units, but not `/usr/lib/systemd/user/`; a legitimate user unit can therefore
fail its path check. `/etc/sudoers.d/` also has no general exception. Do not hide
files in installer-generated state or weaken a working privilege model to evade
validation. Resolve packaging design or ask maintainers about a policy gap.

An app that needs an on-demand background process can use a **transient user
service**, created through `systemd-run --user` with fixed, reviewed arguments.
This uses the normal user manager/cgroup without distributing a static unit or
writing hidden privileged files. Preserve NoNewPrivileges, kill/restart policy,
private umask and stop/recovery hooks. Serialize start/stop, avoid restarting an
active service when a second UI opens, and stop the old service before upgrading.
Test actual service properties, child cleanup, failed start and repeated launches
on the supported systemd version. Archive acceptance alone cannot inspect this
runtime configuration. Mesh's controller is an example; arbitrary intent fields
must never select a unit, command, executable or service property.
Do not assume static-unit specifiers expand inside transient command properties:
the device probe found `%t` remained literal in ExecStopPost. Mesh constructs
the Debian runtime path from the kernel UID instead. Verify the actual cleanup
argument and outcome, not merely that the property was accepted.

These are automated admission checks, not an execution sandbox or a complete
review of shell logic, `.desktop` behavior, dependencies, symlinks or hardware.
Keep the independent [security checklist](08-security-and-publishing.md#pre-publish-checklist).

Documentation size is determined by install rules, not by the folder name:
Mesh 0.1.8 includes Markdown/images under `/usr/share/doc/cardputerzero-mesh/docs`
and explicitly excludes generated PDFs. Check archive contents before claiming
that guides do or do not increase installer size.

## The `czdev` tool and the Store

`czdev` (Python) scaffolds and publishes; it does **not** build the `.deb` (you build with
cmake/cpack or the Python recipe, then hand it the file):

```bash
./czdev login                 # GitHub device-flow auth
./czdev new my-app            # scaffold from the template (renames project/launcher/icons)
./czdev publish --deb build/my-app_1.0.1_arm64.deb   # uploads binary/metadata and opens a PR
./czdev publish --meta-only                        # listing update for an existing app
```

`publish` is a mutation, not a dry run: it can create/use a fork, upload the binary
to a release, commit listing assets/metadata and open a PR against
`CardputerZero/packages`. On merge the Store promotes the accepted binary to its
official release/index. Git contains metadata, not the `.deb`. Run the
[non-publishing preflight](../tools/README.md) first; it performs no authentication,
network requests, install, upload or PR creation. The reviewed CLI has no
`publish --dry-run` option.

`czdev` performs local checks, including a fetched metadata policy. If that fetch
fails, it can skip the metadata precheck; uniqueness is left to server-side CI.
A local CLI success is not evidence that the entire Store gate passed.
The submission records a SHA-256, which PR validation verifies. That checksum
identifies bytes; it is not a developer signature or proof of safe behavior.

Publishing is optional; your own GitHub release is a separate distribution path.
The [release checklist](store-readiness.md) covers the complete workflow and
separates Store admission from hardware/security evidence.

---

Next: if your app drives the LoRa Cap — [optional project sections](projects/README.md). Otherwise skip to
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

## Automate the matching package build

Use a native arm64 CI runner and a container matching the device's Debian release.
Fetch qualified dependency commits explicitly, build and install the real package,
then validate its dependency metadata, executable paths, service files, permissions,
policy helpers and offline regressions. Disable networking and isolate the network
namespace during firewall tests so a test cannot change the host's rules.
Upload a checksummed candidate and corresponding source commit. A successful
artifact job is still separate from RF, camera, GPS and physical cold-boot proof.

Use one authoritative version field and read it from each runtime/build path.
For a split UI/backend app, install that metadata alongside the backend as well
as deriving CMake's project/package version from it. Avoid independent fallback
literals that silently drift when one component is bumped.
Container outputs may be owned by root. Copy them into a runner-owned staging
directory before writing checksums/source metadata and uploading the artifact.
Download the finished artifact and verify both its checksum and source commit.

On upgrade, matching installed-file hashes does not prove the live process loaded
them. Coordinate a restart through the resource owner's lifecycle, then check
its reported version and socket peer PID against the service's MainPID. Starting
an already active unit leaves its old code running. Determine how restart affects
in-flight work and hardware first; do not enable a transmitter or restore privacy
opt-ins merely to produce a healthy-looking status. Verify actual privilege state
and preserved user settings as well as the files.

Inspect supported command-line arguments before a smoke test. Do not assume a
GUI executable implements `--version` or `--help`: an ignored argument can launch
the UI, claim the display/input devices or initialize hardware, especially from
a root installation shell. Use About or package metadata when a version option
is not documented; neither alone establishes which code an existing service has
loaded. A future app can offer an explicit read-only version command that exits
before UI/hardware initialization.

Use a consistent private snapshot for preservation checks. For SQLite, use its
backup facility or another documented consistency method; comparing live database
file bytes can misread WAL/checkpoint activity as data loss. Compare logical rows
and relevant configuration fields, keeping keys and raw records out of public
logs. Classify bookkeeping differences only after inspection, and distinguish
upgrade effects from edits the operator makes during a walkthrough. Do not
restore a whole backup over legitimate new work just to make checksums agree.

Measure optimization on a fixed synthetic workload before and after the change.
Include typical and maximum supported history sizes; separate data preparation
from LVGL rendering, disk writes and RF latency. Use warmups and report medians
without fragile timing thresholds in tests. A headless benchmark can run on the
actual device without opening its radio/camera/display, and should stay outside
the installed app. Reduced work does not establish hours of battery life.

Do not use repeated sudo subprocesses as a long-running health-check transport.
A timeout can make an unprivileged parent attempt to kill a now-elevated child,
causing EPERM and leaving cleanup outside its control. A separate fixed-purpose
capability service can own the privileged probe and publish an atomic verdict.
Validate the record's owner, type, writable modes, boot identity and freshness;
fail closed when it is absent/stale/false. Test the real service identity and
actual rule changes, not just the JSON parser. Remove stale comments and privilege
exceptions when the normal user process no longer needs escalation.

A linked dependency can also bring its own install rules into CPack. Wireless
Surveyor's actual archive audit found LVGL development headers and its static
library under shared include/lib directories, despite the app's own namespaced
install rules. With the project's CMake 3.31 integration, declaring the LVGL
FetchContent dependency `EXCLUDE_FROM_ALL` retained normal dependency linking
and excluded those development payloads from the application installer. Verify
the resulting archive and keep runtime licenses; an intent in CMake is not proof
of package contents.
