# 1. The platform

Before you write a line of code, know what you're building on — it shapes every later decision.

## The device

The CardputerZero is a card-sized handheld built on the **Raspberry Pi CM0** (quad-core Cortex-A53
at 1&nbsp;GHz, 512&nbsp;MB RAM), with a **1.9&quot; 320×170 LCD**, a **46-key keyboard**, a battery,
Wi-Fi, a camera, and expansion for M5Stack's "Cap" add-ons (including a LoRa SX1262 radio). Storage
is microSD.

Three facts dominate app design:

- **The screen is a fixed 320×170.** Tiny and wide. Nothing reflows; you design every screen for
  exactly these pixels.
- **Input is keyboard-only.** No touch, no mouse. All navigation is keys (see
  [the keyboard chapter](05-keyboard.md)).
- **RAM is tight** (~350&nbsp;MB usable) and the stock image swaps even at idle, because a full
  desktop stack runs hidden behind the launcher. Keep your resident set and your buffers small.

## The operating system

It runs **Debian (Trixie) on arm64** — in practice a Raspberry Pi OS base, built with M5Stack's fork
of `pi-gen`. That means the familiar Debian/Raspberry-Pi toolbox is all there: `apt`, `systemd`,
Python 3, SSH, `/sys` and `/dev`, the `gpio`/`spi`/`i2c` groups. If you've shipped software for a
Raspberry Pi, most of your instincts transfer.

Because a complete desktop stack (display manager, panel, file manager, and friends) runs behind the
launcher, some RAM and CPU are already spoken for. Budget accordingly.

## The launcher: APPLaunch

The home screen is **APPLaunch**, an LVGL 9.5 app that runs as a systemd *user* service. It scans
installed apps, shows them in a grid, and launches the one you pick. Two things matter for you as a
developer:

- **APPLaunch is the entry point for your app.** You don't write your own boot/menu; you register
  with APPLaunch (via files your package installs) and it runs you. The contract for that is in
  [how an app lives on the device](02-app-anatomy.md).
- **It hands your app the framebuffer and the keyboard directly.** A graphical app has no text
  console — APPLaunch opens the display and the shared keyboard input device and passes them to your
  process. Your app draws to the framebuffer and reads the same keyboard everything else does.

The launcher grabs the keyboard and **shares** it with the running app (it does not take exclusive
ownership), so your app reads the same evdev device the launcher does.

## The Store

There's a first-party **Store** app for installing community apps. Under the hood it is not an apt
source — it reads a catalog (a JSON registry hosted on GitHub Pages), downloads the chosen app's
`.deb` from a GitHub repository, and installs that local file with `apt`. Dependencies resolve from
the normal Debian/Raspberry-Pi archives.

The practical consequences for you:

- **Everything is a normal `.deb`.** There is no proprietary app format. If you can build a
  well-formed Debian package, you can ship an app — through the Store, or just as a GitHub release
  people install by hand.
- **The Store never runs `apt-get update`.** It installs your `.deb` against whatever package lists
  are already on the device. So any dependency you declare must already be installable from the base
  archives, be legally/operationally maintainable as an app-private bundle, or be
  an explicitly documented external prerequisite with runtime compatibility
  checks. Choose and test the [dependency plan](06-building-and-packaging.md#packaging-a-python-app)
  on a fresh supported image; a description alone does not install a dependency.

Publishing to the Store is optional — you can distribute entirely through your own GitHub releases.
But even if you do, matching the Store's conventions (honest metadata, a real icon, 320×170
screenshots, no root) is what makes an app look trustworthy.

## What "good" means here

Throughout this guide, a *good* app is one that:

- reads cleanly at 320×170 and is fully usable from the keyboard,
- feels native — it looks like it belongs next to the built-in apps,
- runs unprivileged (or escalates narrowly and honestly),
- is open, reproducible, and ships its licenses and attributions,
- and never pretends to do less than it does.

The rest of this guide is how to get there. Start with [how an app lives on the
device](02-app-anatomy.md).
