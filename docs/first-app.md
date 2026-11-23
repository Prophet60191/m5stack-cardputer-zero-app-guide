# First app: build the official counter

Build the official Template, open its counter, make one small change, and inspect
a device package. This is a learning example, **not a new production utility or a
Store-ready app**. It needs no radio, account, Cap, Python backend or service.

The example uses the official Template's existing shell, input routing, themes,
assets, model/viewmodel and screens. We deliberately reuse them rather than
creating another starter framework. No keyboard patch is needed for this
navigation-only example; full text entry is a separate [input decision](05-keyboard.md).

## 1. Prepare your desktop

Use a working C++17 compiler, Git, Ninja and **CMake 3.31 or newer**. Desktop builds
also need SDL2, FreeType, PNG, JPEG, fmt and zlib development files. On macOS with
Homebrew, the [official Template instructions](https://github.com/CardputerZero/Template/blob/477fa6d217b683e3084c361a757f03dc8ca9f753/README.md)
list these dependencies:

```bash
brew install cmake ninja sdl2 freetype libpng jpeg fmt zlib
git --version
cmake --version
```

Linux dependency names and the broader build paths are in
[chapter 6](06-building-and-packaging.md#develop-in-the-desktop-simulator--and-why).
Check the actual CMake version: a distribution's default package may be older
than 3.31. Install dependencies as a separate, deliberate setup step; the Store
preflight never installs them for you.

## 2. Get reviewed source

From a working directory of your choice, use new directory names:

```bash
git clone https://github.com/CardputerZero/Template.git first-counter
git -C first-counter checkout --detach 477fa6d217b683e3084c361a757f03dc8ca9f753
git clone https://github.com/lvgl/lvgl.git first-counter-lvgl
git -C first-counter-lvgl checkout --detach 85aa60d18b3d5e5588d7b247abf90198f07c8a63
cd first-counter
git rev-parse HEAD
```

These commands download source. The pinned revisions make the walkthrough
repeatable; they are not a claim that newer upstream changes are unnecessary.
Compare later revisions before adopting them. The LVGL revision is the v9.5.0
source used for this example. Keep upstream MIT notices and asset licenses.

## 3. Build and open the desktop example

For an Apple Silicon Mac:

```bash
cmake --preset darwin-arm64 \
  -DFETCHCONTENT_SOURCE_DIR_LVGL="$PWD/../first-counter-lvgl"
cmake --build --preset darwin-arm64-dbg --parallel 4
./build/darwin-arm64/Debug/template_app
```

The result is an SDL simulator window containing the device UI, not a Debian
installer. Keep the terminal open to see startup errors. If configuration fails,
check the first missing dependency and CMake version; do not solve a missing
library by running the application as root.

For Linux x86-64, use `linux-x86-64` and `linux-x86-64-dbg` instead, then run
`./build/linux-x86-64/Debug/template_app`. This alternative is supplied by the
pinned official presets but was not freshly executed for this walkthrough.

Try the following in the focused simulator window or its virtual keyboard:

1. On the first page, use **8** to open the counter.
2. Use **C/Right** twice: the counter should show 2.
3. Use **Z/Left** three times: it should stop at 0.
4. Tap **Esc** to return. On the first page, **6** changes the theme.
5. Reopen the counter; its value remains for this running session. Hold **Esc**
   on the first page to exit. A fresh process starts at 0.

These keys come from the pinned
[input router](https://github.com/CardputerZero/Template/blob/477fa6d217b683e3084c361a757f03dc8ca9f753/src/platform/linux_input.cpp)
and [navbar](https://github.com/CardputerZero/Template/blob/477fa6d217b683e3084c361a757f03dc8ca9f753/src/view/widgets/navbar.cpp),
not a guessed keyboard map. Check the specific counter shortcuts: the first
page's 4–8 actions are not its counter-page controls.

## 4. Make one visible change

Close the simulator. In `src/model/base_model.cpp`, change only the greeting
returned by `BaseModel::greeting()` from `Hello World` to `My first counter`.
Then rebuild and launch with the same commands from step 3. The first page should
show the new text. Check both themes and return from the counter. `git diff`
should show only that greeting change.

The path from action to pixels is small: the navbar calls a viewmodel action;
`counter_subject_` holds this demo's session value; `ButterScreen` binds its label
to that subject. The greeting comes from the model, published by the viewmodel
and bound on the first screen. The existing screen manager owns screen changes.
You do not need another process to understand or extend this example.

This demo is not a durable counting application. Before relying on it for real
work, define a maximum count, persistence/reset behavior and recovery from write
failure. Its increment action is not bounded for indefinite use; do not confuse
this short exercise with production acceptance testing.

## 5. Build an arm64 package without using the device

Continue only if you need the device artifact now. Desktop build success does
not produce an arm64 binary. Use a **separate Debian 13 arm64 environment**, such
as an isolated container/VM; do not install build dependencies on your handheld
for this exercise. Copy the Template and LVGL source into that environment as
sibling directories named `first-counter` and `first-counter-lvgl`.

Install the build dependencies there, then work as an ordinary user:

```bash
sudo apt-get update
sudo apt-get install --no-install-recommends \
  build-essential cmake ninja-build dpkg-dev \
  libfreetype-dev libpng-dev libjpeg-dev libfmt-dev zlib1g-dev
uname -m
cmake --version
cd first-counter
cmake -S . -B build/arm64 -G Ninja \
  -DCMAKE_BUILD_TYPE=Release -DUSE_DESKTOP=OFF \
  -DAPP_USE_DRM=OFF -DCM0_SDK_ROOT=/ \
  -DCM0_ALLOW_FETCH_DEPS=OFF \
  -DFETCHCONTENT_SOURCE_DIR_LVGL="$PWD/../first-counter-lvgl" \
  -DAPP_INSTALL_SYSTEMD_SERVICE=OFF
cmake --build build/arm64 --parallel 4
(cd build/arm64 && cpack)
dpkg-deb --info dist/TemplateApp_0.2.1_rev1_arm64.deb
dpkg-deb --contents dist/TemplateApp_0.2.1_rev1_arm64.deb
```

`uname -m` must report `aarch64` for this native arm64 recipe. `/` is the dependency
root **inside that Debian arm64 environment**, not a macOS sysroot or a cross
compiler setting. The package is written to the Template's `dist/` directory.
We disable the optional system service: this foreground demo needs none.
These commands explicitly compile reviewed source; they are separate from the
non-executing [Store preflight](../tools/README.md).

## 6. Inspect before installing or publishing

Check that the package architecture is arm64, the desktop entry has
`Terminal=false`, and its executable is `/usr/bin/template_app`. You can inspect
package content in an isolated environment without installing or running it.
No system service should be included with the option used above.

**Do not install this demo over an existing Template-based app.** It still uses
the Template binary, config, icon and metadata identities. A different display
name alone does not prevent file collisions. To make a real app, first give the
CMake project/executable, asset namespace, desktop/icon paths, config path,
Debian identity and `app-builder.json` coherent unique names. Replace placeholder
maintainer/store data, preserve licenses, check actual runtime dependencies, and
follow [app anatomy](02-app-anatomy.md) and [Store readiness](store-readiness.md).
The demo's placeholder maintainer is intentionally not a real person's identity.

Only then plan installation, launch/back behavior, physical keys and upgrade/data
preservation checks using [chapter 6](06-building-and-packaging.md). A device check
should verify the exact installed artifact; no flashing or radio changes are
needed for a counter. Store acceptance is a later, separate step.

## Verification and limits

Maintainer check on **2026-11-22**, using the pinned sources above:

- macOS arm64 desktop Debug build succeeded. Headless SDL startup remained alive
  for three seconds and exited cleanly when terminated. That is a startup smoke
  check, not the interactive sequence in step 3.
- The greeting edit was rebuilt successfully; the diff and compiled executable
  contained the new text. Visual confirmation remains a reader check.
- Debian 13 arm64 Release build and CPack packaging succeeded in a network-disabled
  container using already provisioned build dependencies. Package control/payload
  inspection confirmed arm64, foreground desktop entry and no systemd service or
  install/remove maintainer scripts. No package was installed on a device.
- A fresh dependency installation/container-image build, Linux desktop run,
  interactive simulator walkthrough, physical keyboard check and
  [independent-reader exercise](first-reader-check.md) remain unperformed here.

The source/package checks show that the example can compile and package in those
specific environments. [The evidence record](first-app-evidence.json) pins the
source, one-line edit, tool versions and inspected package hash. They do not prove that a new reader can follow it unaided,
that a renamed app is release-ready, or that any peripheral works.

[Short route](start-here.md) · [Choose the next capability](projects/README.md)
