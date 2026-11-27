# First app: build the official counter

Build the official Template, open its counter, change the greeting, then add a
working reset action. Optional: build and inspect a device package. This is a learning example, **not a new production utility or a
Store-ready app**. It needs no radio, account, Cap, Python backend or service.

The example uses the official Template's existing shell, input routing, themes,
assets, model/viewmodel and screens. I deliberately reuse them rather than
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

**Official foundation:** CardputerZero Template and its pinned LVGL dependency.

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

**Official foundation:** Template presets, simulator, built-in counter and normal keyboard routing. The particular walkthrough and evidence below are the guide contribution.

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

**Guide exercise:** Change one greeting in the official Template; the model and viewmodel are upstream.

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

## 5. Add a reset action

**Guide contribution:** Add one callback and input slot while keeping Template’s event path and display binding.

Now change behavior, not just text: pressing **6** on the counter page should
set the count to zero. On the home page, **6** should still switch themes. The
official example already routes this key and binds the label to the count, so
there is no need to add a driver, create a new screen or redraw the label
yourself. Close the simulator and make these edits in `first-counter`.

1. **Give the viewmodel an action.** In `src/viewmodel/base_viewmodel.h`, add
   `void reset_counter();` immediately above `void increment_counter();`. In
   `src/viewmodel/base_viewmodel.cpp`, add this above the existing increment
   method:

   ```cpp
   void BaseViewModel::reset_counter() {
       counter_subject_.set(0);
   }
   ```

2. **Route the key on the counter page only.** In
   `src/platform/linux_input.cpp`, find `nav_key_to_index()`. Inside the
   first switch, the one under `if (nav_shortcut_mode)`, add this case.
   Leave the second switch (home page) as it is:

   ```cpp
   case '6':
       return 2;
   ```

3. **Connect slot 2 to the action.** In `src/view/widgets/navbar.h`, add
   `static void reset_counter_cb(lv_event_t* event);` next to
   `increment_counter_cb`. In `src/view/widgets/navbar.cpp`, replace the
   middle entry (index 2) in `butter_icons` with `{"", reset_counter_cb},`.
   Add `lv_obj_remove_event_cb(button->root(), reset_counter_cb);` immediately
   above the existing line that removes `increment_counter_cb`. This cleans
   up the old handler when switching screens. Add this definition immediately
   above `NavBar::increment_counter_cb()`:

   ```cpp
   void NavBar::reset_counter_cb(lv_event_t* event) {
       auto* view_model = static_cast<viewmodel::BaseViewModel*>(lv_event_get_user_data(event));
       if (view_model) {
           view_model->reset_counter();
       }
   }
   ```

4. **Show people what to press.** In `navbar.cpp`, change the size of
   `kButterShortcuts` from 3 to 4 and insert `{"6", "Reset"},` between the
   Less and More entries. To keep all four hints readable on 320×170,
   shorten those two key labels from `Z/Left` and `C/Right` to `Z` and `C`.
   The arrow keys still work and remain in Help. In `navbar.h`, change the size of
   `shortcut_key_labels_` from 3 to 4 so it has room for the new hint. In
   `src/view/widgets/help_popup.cpp`, change the size of `kButterRows` from
   3 to 4 and insert `{"6", "Reset to zero"},` between Decrease and Increase.

5. **Rebuild and try it.** Run the same build and launch commands as step 3.
   Press **8** to open the counter, press **C/Right** twice, then press **6**.
   You should see `Counter: 2` change immediately to `Counter: 0`.
   Press **C/Right** once and **Z/Left** once to check the original controls.
   Tap **Esc** to go home and press **6** there: it should still change the
   theme. Check that the counter footer fits in both themes.

Follow the action you added: **key → navigation slot → callback → viewmodel →
counter label**. If the reset appears in the footer but does nothing, check
that the new key maps to index 2 in the first switch and that index 2 in
`butter_icons` points at the reset callback. If the counter changes, the
existing subject binding takes care of updating the label.

<a id="5-build-an-arm64-package-without-using-the-device"></a>

## 6. Build an arm64 package without using the device

**Adapted:** Reuse the Template packaging implementation; the pinned native ARM64 container recipe and package inspection are guide work.

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
The command disables the optional system service: this foreground demo needs none.
These commands explicitly compile reviewed source; they are separate from the
non-executing [Store preflight](../tools/README.md).

<a id="6-inspect-before-installing-or-publishing"></a>

## 7. Inspect before installing or publishing

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

For the next hands-on step, use the separately named [first device app](first-device-app.md) instead of installing this Template artifact. The [packaging chapter](06-building-and-packaging.md) covers the general release checks. A device check
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
  manual end-to-end walkthrough, physical keyboard check and
  [independent-reader exercise](first-reader-check.md) remain unperformed here.

**Why add this exercise?** The official Template shows a counter and its normal controls. The guide adds one feature so a beginner can follow an input all the way to the model and display without writing a new app framework. The unchanged Home shortcut is part of the test because keys should not change meaning outside the current screen.

The reset extension was checked separately in a temporary pinned Template copy
on Apple Silicon. The Debug build succeeded. Synthetic desktop input exercised
the simulator's normal event handler: opening the counter, going from 0 to 2,
resetting to 0, incrementing and decrementing again, going back, and switching
the home theme with the same key. The counter footer was visually inspected at
320×170 in both themes. The reset extension was not installed on a device; the
arm64 package above was verified for the greeting edit, not the reset extension.

The source/package checks show that the example can compile and package in those
specific environments. [The evidence record](first-app-evidence.json) pins the
source, one-line edit, tool versions and inspected package hash. They do not prove that a new reader can follow it unaided,
that a renamed app is release-ready, or that any peripheral works.

[Short route](start-here.md) · [Choose the next capability](projects/README.md)
