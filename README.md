<h1 align="center">Building Apps for the M5Stack Cardputer Zero</h1>

<p align="center">
  A practical, opinionated guide to writing <b>good</b> native apps for the
  M5Stack CardputerZero — the card-sized Raspberry&nbsp;Pi&nbsp;CM0 Linux handheld.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/device-M5Stack%20CardputerZero-red?style=flat-square" alt="device">
  <img src="https://img.shields.io/badge/UI-LVGL%209.5-064F8C?style=flat-square" alt="lvgl">
  <img src="https://img.shields.io/badge/package-Debian%20.deb-A81D33?style=flat-square" alt="deb">
  <img src="https://img.shields.io/badge/docs-CC--BY--4.0-green?style=flat-square" alt="license">
</p>

---

## Why this exists

The CardputerZero is new, and its app-development story is spread across a template repo, a
publishing tool, and whatever you can reverse-engineer from the built-in apps. This guide pulls that
together into one path — from "what even *is* an app on this device" to a polished, trustworthy
release — written while actually shipping one.

It is deliberately **opinionated**. It doesn't just list options; it tells you the approach that
holds up on *this* hardware (a fixed 320×170 screen, a 46-key keyboard, ~350&nbsp;MB of RAM that
swaps at idle, no touch) and why. Where a decision cost real debugging to get right, that's called
out so you don't pay for it twice.

## The worked example

The worked example is a real app whose code and regression checks accompany the guide:
**[M5Stack Cardputer Zero Mesh App](https://github.com/Prophet60191/m5stack-cardputer-zero-mesh-app)**
— a Meshtastic client for this device, built exactly this way (native LVGL UI + a separate
radio supervisor), with fixes and regression evidence from an independent security review. Its security
documentation distinguishes simulator/container checks from device qualification. When a chapter says "see the
worked example," that's the repo to read.

## Who it's for

Makers and developers who can read C++ and/or Python and want their CardputerZero app to feel
*native* — like it belongs next to the built-in apps — rather than thrown together. You do **not**
need prior LVGL or Debian-packaging experience; both are covered.

## Contents

1. **[The platform](docs/01-platform.md)** — the OS, the APPLaunch launcher, the Store, and the
   constraints that shape every decision.
2. **[How an app lives on the device](docs/02-app-anatomy.md)** — an app is a `.deb`; the launcher
   contract; the least-privilege model; how apps reach the hardware.
3. **[An architecture that works](docs/03-architecture.md)** — native LVGL UI + a separate
   supervisor over a local intent socket. The single most important pattern in this guide.
4. **[UI and polish](docs/04-ui-and-polish.md)** — LVGL 9.5 on 320×170, MVVM + reactive binding,
   navigation, theming, and the anti-slop checklist.
5. **[The keyboard](docs/05-keyboard.md)** — the 46-key layout, the Shift / Fn / Sym modifiers, and
   the official complete symbol map, reusable decoder and raw-event tests for reliable text input.
6. **[Building and packaging](docs/06-building-and-packaging.md)** — the desktop simulator, the
   device cross-build, the `.deb` (C++ *and* Python recipes), `app-builder.json`, and `czdev`.
7. **[Radio bring-up](docs/07-radio-bring-up.md)** — if your app drives the LoRa Cap: the robust
   SX1262 power/init/teardown sequence, done from userspace with no root.
8. **[Security, licensing and publishing](docs/08-security-and-publishing.md)** — least privilege,
   no secrets, honest disclosure, the MIT/GPL split, integrity, attribution, and a pre-publish
   checklist.

New to the device? Read 1 → 2 → 3 in order, then dip into the rest as you build.

## How to use it

Keep the [worked-example repo](https://github.com/Prophet60191/m5stack-cardputer-zero-mesh-app) open
alongside these chapters. The guide explains the *why* and the shape; the repo shows the *exact*
code. Together they should get you from zero to a published, native-feeling app.

## Contributing

Corrections and additions are welcome — open an issue or a PR. This device is young and the
collective knowledge is still forming; if you learned something the hard way, it belongs here.

## License

This guide is licensed **[CC BY 4.0](LICENSE)** — use it, adapt it, build on it, with attribution.
Code snippets within it are provided as examples you may use freely.

> **Meshtastic®** is a registered trademark of Meshtastic LLC. **M5Stack** and **Cardputer** are
> trademarks of their respective owners. This is an independent community guide, not affiliated with
> or endorsed by either.
