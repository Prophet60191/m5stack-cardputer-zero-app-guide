# Start from the reusable App Shell

The shell is a small native Cardputer Zero sample with three destinations:
**Start**, **Settings** and **About**. Its purpose is to give you a working
launch point, not to make you reverse-engineer Tick & Bell or adopt a particular
menu design. The carousel is my preference and a demonstration, not an M5Stack
requirement. A direct list may suit your app better.

![App Shell on the Start menu in the desktop simulator](images/app-shell-home.png)

The screenshot shows the simulator’s sample 100% battery value, not a hardware reading.

Keep the shell repo's README next to you for commands. This page is the source
of truth for how the pieces fit, what to customize, and what to verify.

## Start without extra moving parts

1. Run the unchanged shell in the desktop simulator. Move left from Start
   to About and right back to Start. Open each destination with Enter.
   Esc returns without losing the selected item. Open the help screen and
   return to the page you were on.
2. Change one title and its description in `src/app/starter_ui.h`. Build again
   and check the longest text you plan to use in both themes. Keep home labels
   brief; explanations belong on the destination screen.
3. Change the example content on the Start page, then add your useful first
   action. Keep selection/key routing and rendering separate. Don't introduce
   a service, Python or a device peripheral unless your app needs one.

## Know which files you own

| Where | What it controls |
| --- | --- |
| `src/app/starter_ui.h` | The example menu entries, destination content, data handed to the visual component, and the app's use of the official key router. |
| `src/app/starter_navigation.h` | Which destination is open, wraparound and what Back and Help do. The small navigation test does not depend on hardware. |
| `src/shared/home_menu.h` | The reviewed, vendored copy of the guide's [home-menu component](../examples/ui-patterns/carousel-position/README.md). The guide owns the pattern, including typography, battery and keyboard hints. |
| `src/shared/page_shell.h` | Reusable theme tokens, font roles, fixed page header/footer, and a keyboard-scrolled list. Visual defaults are a starting point. |
| `src/platform/linux_input.cpp` and `keyboard_decoder.*` | The Template’s evdev path with the reviewed extension for text and the official device keymap. Apps using the official shared runtime should not decode its keys again. |
| `app-identity.cmake` | Visible name, unique Debian package/launcher ID, version and maintainer. Start with a fresh build directory after changing identity. |
| `cmake/cm0-package.cmake` | Package and launcher layout. Learn what it installs before adding any startup behavior or permissions. |

The official CardputerZero Template still owns display startup, platform
key mapping, screenshot handling and the theme preference flow. The shell
uses that foundation and swaps in its own foreground UI. The app supplies a
measured battery percentage to the shared home menu when one exists; the
desktop value is simulated. Never invent a reading when the device is missing one.

## Use the page and keyboard building blocks

The shell repo is the buildable library. This guide documents what the pieces
do and which choices are optional. Use a fixed header and footer with a clipped
content region, shared light/dark colors, and one font role per job: 10 px
secondary text, 12 px body and controls, and 16 px section titles. The
**About** list demonstrates selection, wrapping and a position indicator that
appears only on overflow. Compare actual app screens before locking a row style.

The **Start** page has a sample label editor. Enter opens it; Enter keeps the
label for the current run and Esc discards the draft. Bare C, Z, F, X, H and
digits are text while editing, not shortcuts. Fn+H opens Help without changing
the draft, and Esc returns to the editor. This is a sample of input ownership,
not a prescribed edit form layout. See the [keyboard chapter](05-keyboard.md)
for official Fn, Sym and position details. Do not invent a new keymap.

## Make a package that can sit beside the sample

Pick a different lowercase package ID and visible name in
`app-identity.cmake`, then configure in a new build directory. The ID becomes
the executable, launcher filename, icon name and preferences directory. Verify
all four change, not just the title. Using a unique ID prevents your test
package from replacing another app or reusing its preferences.

Start with the [building and packaging chapter](06-building-and-packaging.md)
for dependencies and [the first-device walkthrough](first-device-app.md) for
copying the package, verifying installation, upgrading and removing a test app.
The shell is not a Store listing. Use [Store readiness](store-readiness.md)
only when you are actually preparing a submission.

## Check the result

- In both themes, confirm text reads comfortably at 320×170, the dot follows
  selection in both directions, and the displayed shortcuts work.
- Open a destination, return, and confirm selection is retained. Test Help and
  exit from home. Close and reopen to verify the saved theme.
- Inspect the arm64 package for the expected identity and launcher path.
  Then test the physical keypad and display on the intended Cardputer Zero.
  A simulator run does not qualify those checks.

If the simulator works but the installed app does not, start with
[device app troubleshooting](device-app-troubleshooting.md). For a fuller
example with its own scheduler, see [Tick & Bell](case-studies/tick-bell.md).
