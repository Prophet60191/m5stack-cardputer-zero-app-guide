# The counter demo is installed. What went wrong?

Use this page alongside the [first-device app walkthrough](first-device-app.md). Start with what you see. Check the **same `.deb`** you intended to install and
change one thing at a time. A good desktop run is useful evidence, but it does not
test APPLaunch, the device keyboard, or the libraries on the handheld.

**Why add this page?** The official tools describe build and submission requirements. This guide starts from the symptom on the handheld, because a valid package can still have a wrong launcher entry, an unresolved library, or different key behavior. The checks narrow the problem without reimaging the device or changing unrelated packages.

## No app icon in APPLaunch

On the CardputerZero, check the package and the files it owns:

```sh
dpkg-query -W -f='${db:Status-Abbrev} ${Package} ${Version} ${Architecture}\n' cp0-guide-counter-demo
dpkg-query -L cp0-guide-counter-demo | grep '/APPLaunch/'
```

Look for `ii` (installed), the version you intended, and an entry under
`/usr/share/APPLaunch/applications/` for **Guide Counter**. Open **that
package's** `.desktop` file and
check `[Desktop Entry]`, `Name`, `Exec`, `Icon`, and `Terminal=false`.
Confirm `Exec` resolves to this app's executable (not another app's) and `Icon`
resolves relative to `/usr/share/APPLaunch/`. See
[the launcher contract](02-app-anatomy.md#the-desktop-entry). If the entry is
wrong, fix the package source rather than editing launcher-owned files or
borrowing another package's name.

## The icon is there, but the app closes immediately

Note the time, launch once from APPLaunch, and look only at the matching startup
lines. From a terminal in your regular device session, use the launcher’s user unit:

```sh
journalctl --user -u APPLaunch.service --since '2 minutes ago' -n 25 --no-pager
```

If that produces nothing, confirm the launcher unit for your image with
`systemctl --user list-units --type=service`. An empty log or an access error
does not prove the app ran. Use the first relevant error: a missing path points
to package layout; a named missing `.so` points to a runtime dependency. The
launcher can hand off display and keyboard settings that an SSH command does
not, so running the binary remotely is not an equivalent launch test.

For example, an earlier official Camera build expected `libcamera.so.0.7`, but
the device image had libcamera 0.8. The startup error identified a library
mismatch, not a broken sensor. [Camera v1.0.4](https://github.com/CardputerZero/Camera/releases/tag/v1.0.4)
documents its move to libcamera 0.8. That was a Camera fix, not a dependency of
this counter. Don't symlink incompatible libraries to silence the message.

### If the executable is there, check what Linux can load

M5Stack’s [launcher documentation](https://github.com/CardputerZero/launcher/blob/d59f15918c473bc61de13b4960d69ce0e7514899/README.md) shows how to check the launcher service, and the [Developer Center](https://dev.cardputer.cc/) checks the package before upload. Neither check tells you whether **your app’s executable can find its shared libraries on this device image**.

On the Zero, as your regular user, use the executable path from your app’s
`Exec` line, without the arguments. This example uses the Guide Counter path.
Use `ldd` only on an executable you built or trust; don't run it on a stranger's
download.

```sh
app=/usr/bin/cp0-guide-counter-demo
test -x "$app" && file "$app"
# For a trusted, dynamically linked ARM aarch64 Linux executable:
LC_ALL=C ldd "$app"
```

- **Missing path or not executable:** Check the package contents and the
  `Exec` path. If it points to a script, check the script’s interpreter and
  the native executable it calls instead.
- **`libexample.so.1 => not found`:** The executable exists, but Linux cannot
  resolve that library version. If it should come from the device image, check
  which package supplies the compatible version and declare it in the app’s
  dependencies. If it’s your own library, check that the package contains it
  and that the executable can find it. Rebuild, then check the same executable
  path again. Don't symlink a different version or change system library paths
  to get past the error.
- **All libraries resolve:** That rules out a missing startup library in this
  check, not a display, input, or startup problem. Return to the launcher
  journal and the first error from that launch.

**Verified on a Cardputer Zero:** A disposable arm64 package left out its own
test library. Its executable existed and had the right architecture, but
`ldd` reported the library missing and the process exited before running the
app. After rebuilding the package with the matching library, the same check
resolved it and the executable exited successfully. Both packages were
extracted to temporary folders, not installed. This verifies the dependency
check on hardware, not a full APPLaunch or display test.

## It works on the desktop, but not on the device

On a machine with Debian package tools, inspect the artifact without installing:

```sh
dpkg-deb -f ./your-demo.deb Package Version Architecture Depends
dpkg-deb -c ./your-demo.deb
```

Check for `arm64`, the correct package and files, and dependencies intended for
the supported device image. On the device, if `file` is available, use it on
the executable resolved from `Exec` (not the `.desktop` file or the `.deb`). A
native device executable should be an ARM aarch64 Linux ELF; if `Exec` points to
a script, check its interpreter and the binary it invokes instead. An `arm64`
package label does not turn a desktop binary into a device build. See
[cross-building and packaging](06-building-and-packaging.md).

## Menus open, but the keys do the wrong thing

Start with a short single press and no locked modifiers. From **About** (the
home screen), press **8** to open **Counter**. In **Counter**, try **C** (right)
and **Z** (left), then tap **Esc** to go back. Test **hold Esc** separately on
**About** to exit to the launcher; it is not the same as the short back press.
If navigation works but the count doesn't change, record the screen and one key
that failed before changing mappings. Use the [official key map and input checks](05-keyboard.md)
to compare simulator and hardware; don't turn a mapping issue into a permission fix.

If asking for help, share the package version and architecture, image version,
screen, expected result, and one relevant error line with usernames, device or
network identifiers, and personal paths removed. Don't post a raw journal or
delete saved data while diagnosing. The steps here are inspection only; they do
not require root, a factory reset, or an OS reflash.
