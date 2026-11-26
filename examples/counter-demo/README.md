# Guide Counter demo source

Guide Counter is a tiny teaching app for the Debian arm64 Cardputer Zero.
**About** tells you which version you launched. **Counter** adds or subtracts
one and saves the result. There are no accounts, services, networking
requirements or extra hardware. The example is separate from the original
Template counter and is not a Store submission.

I use a small [patch](counter-demo.patch) against the exact
[official Template revision](https://github.com/CardputerZero/Template/tree/477fa6d217b683e3084c361a757f03dc8ca9f753)
rather than copying the framework. The upstream MIT and asset notices still
apply. Keep them with any source or package you redistribute. The [demo code
and model test are MIT](LICENSE).

## Build in the simulator

From the root of a checkout of this guide, copy the patch to a new workspace
and apply it to the pinned Template source. Obtain the pinned LVGL source too:

```sh
patch_file="$PWD/examples/counter-demo/counter-demo.patch"
work=$(mktemp -d)
git clone https://github.com/CardputerZero/Template.git "$work/counter"
git -C "$work/counter" checkout --detach 477fa6d217b683e3084c361a757f03dc8ca9f753
git -C "$work/counter" apply --check "$patch_file"
git -C "$work/counter" apply "$patch_file"
git clone https://github.com/lvgl/lvgl.git "$work/lvgl"
git -C "$work/lvgl" checkout --detach 85aa60d18b3d5e5588d7b247abf90198f07c8a63
cd "$work/counter"
```

Stop if a clone, revision checkout or patch check fails. Use a fresh directory
rather than applying the patch over another app. For an Apple Silicon Mac with
the [desktop dependencies](../../docs/first-app.md#1-prepare-your-desktop):

```sh
cmake --preset darwin-arm64 -DGUIDE_COUNTER_VERSION=0.1.0 \
  -DFETCHCONTENT_SOURCE_DIR_LVGL="$PWD/../lvgl"
cmake --build --preset darwin-arm64-dbg --parallel 4
demo_state=$(mktemp -d)
XDG_STATE_HOME="$demo_state" ./build/darwin-arm64/Debug/cp0-guide-counter-demo
```

Using the same `demo_state` for your next launch lets you verify the count
was saved across processes without using your usual account's state directory.
Run [the exercise](../../docs/first-device-app.md) for the keys and expected result.
The simulator cannot prove how the handheld launcher or physical keys behave.

## Build two arm64 packages

Copy the patched `counter` source and pinned `lvgl` source as sibling
directories to a **Debian 13 arm64** build environment with the
[device build dependencies](../../docs/first-app.md#6-build-an-arm64-package-without-using-the-device).
They do not belong on the handheld. Start in the patched `counter` directory
and confirm `uname -m` reports `aarch64`:

```sh
for version in 0.1.0 0.2.0; do
    build="build/arm64-$version"
    cmake -S . -B "$build" -G Ninja \
      -DCMAKE_BUILD_TYPE=Release -DUSE_DESKTOP=OFF \
      -DAPP_USE_DRM=OFF -DCM0_SDK_ROOT=/ -DCM0_ALLOW_FETCH_DEPS=OFF \
      -DFETCHCONTENT_SOURCE_DIR_LVGL="$PWD/../lvgl" \
      -DAPP_INSTALL_SYSTEMD_SERVICE=OFF -DGUIDE_COUNTER_VERSION="$version" || break
    cmake --build "$build" --parallel 4 || break
    (cd "$build" && cpack) || break
done
ls -l dist/cp0-guide-counter-demo_*_rev1_arm64.deb
```

The result is two versions of the same Debian package. Version 0.2.0 changes
the version shown in About but not the saved data format. The state is a bounded,
plain integer in `$XDG_STATE_HOME/cp0-guide-counter-demo/count` (or the same path
under `~/.local/state`). This is intentionally not a database or an example of
downgrading an incompatible data format. The sample manifest illustrates local package identity only; it is not a matching
Store manifest for both versions. Do not submit this teaching package to the Store.

Next: [inspect, install, upgrade and remove the demo](../../docs/first-device-app.md).

## Optional storage test

Run this from the guide checkout after getting the patched source above,
in the same shell where `work` points to that workspace:

```sh
test_dir=$(mktemp -d)
c++ -std=c++17 -Wall -Wextra -Werror -I "$work/counter/src/model" \
  examples/counter-demo/check_counter_store.cpp -o "$test_dir/check"
"$test_dir/check" "$test_dir/state"
```

This tests the model with disposable files. It does not check the launcher,
the physical buttons, hardware permissions, or sudden power loss. The demo
is single-instance and uses a same-directory file replacement for ordinary
restarts. A failed write leaves the previous count on screen; an invalid existing
file loads as zero.
