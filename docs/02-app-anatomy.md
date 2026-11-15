# 2. How an app lives on the device

An app on the CardputerZero is a **Debian package**. There is no special "app format" — the launcher
just reads standard files that your `.deb` drops in known places. So the whole job of "shipping an
app" is: build a well-formed `.deb` that contains the right pieces. This chapter is what those pieces
are, learned by taking the device's own apps apart (they're the reference for doing it right).

## An app is a `.deb`

Every app — the built-in ones and the Store ones — is a `.deb` installed with `apt`/`dpkg`. Store
apps are the same kind of package; they just *additionally* carry catalog metadata
(`app-builder.json`). So everything below is simply "what a good package contains."

## Where the pieces go

A typical app installs this layout:

| Path | Purpose |
|---|---|
| `/usr/share/APPLaunch/bin/<Binary>` | the executable |
| `/usr/share/APPLaunch/applications/<app>.desktop` | the launcher entry (how it appears and starts) |
| `/usr/share/APPLaunch/share/images/<app>.png` | the icon, referenced from the `.desktop` relative to `/usr/share/APPLaunch/` |
| `/usr/share/<App>/…` | app data/assets (fonts, sounds, images) — not next to the binary |
| `/usr/share/doc/<pkg>/LICENSE`, `THIRD_PARTY_NOTICES.md` | license and attributions, **shipped inside the package** |
| `/etc/sudoers.d/<pkg>` | *only* for an app that genuinely needs root — a narrow grant (see [Privilege model](#the-privilege-model)) |

Conventions worth copying: a descriptively named binary; the icon as a PNG under `share/images/`;
bulky assets under `/usr/share/<App>/`; docs (license + notices) under `/usr/share/doc/<pkg>/`.

## The `.desktop` entry

This is the launcher contract — minimal and strict. For a graphical, unprivileged app:

```ini
[Desktop Entry]
Name=My App
Exec=/usr/share/APPLaunch/bin/My-App
Icon=share/images/my-app.png
Terminal=false
Type=Application
```

Key points:

- **`Terminal=false` is load-bearing.** It tells APPLaunch this is a framebuffer app and to hand it
  the display and keyboard directly (via environment variables the launcher sets) — there is no text
  console. A graphical app that sets `Terminal=true` will not get a usable surface.
- **`Icon` is relative** to `/usr/share/APPLaunch/`.
- **No `Categories` line** on the device — categories live in the Store catalog, not in the
  on-device `.desktop`.

### What the launcher validates

APPLaunch scans `/usr/share/APPLaunch/applications/*.desktop` and **rejects** an entry that is
missing `Name` or `Exec`, has an invalid `Icon`, duplicates another app's `Exec` (first one wins),
shadows a built-in app, or uses an "unsafe" `Exec` (it checks the command against a safety policy, so
you can't point it at an arbitrary shell command). Design to that contract: a valid `Name`, `Exec`,
and `Icon`, a unique `Exec`, and don't try to override a built-in.

## The privilege model

This is the most important thing to get right, and the thing the publish tooling actually enforces.
**Most apps need no root at all.** The device user is already in the `gpio`, `spi`, and `i2c` groups,
so SPI, GPIO, and I²C all work unprivileged. Escalate *only* for the few things that truly require it
(raw sockets, monitor mode, firewall rules), and do it narrowly.

- **No root (most apps):** `Exec` points straight at the binary. No `sudoers` file. `Depends` lists
  only the libraries you actually use.
- **Root, when truly needed:** three things together —
  1. `Exec=/usr/bin/sudo -n -- <binary>` in the `.desktop`,
  2. a shipped `/etc/sudoers.d/<pkg>` granting **passwordless sudo for that one binary only**,
  3. `sudo` in `Depends`.

  The `-n` (non-interactive) means it fails fast if the rule is missing rather than hanging, and the
  grant is scoped to the single binary — never a blanket rule.

A bundled `systemd` service that runs as **root is rejected** by the publish validator. Never ship a
blanket `NOPASSWD: ALL`. If you need a privileged helper, prefer — in order — **file capabilities**
(`setcap cap_net_raw+eip` on just the binary that needs raw sockets), then a **scoped, sandboxed
`systemd` unit** started through a narrow policy, then — only where capabilities can't reach — a
root-owned wrapper that **re-validates every argument**. The least-privilege ladder is covered in
[security and publishing](08-security-and-publishing.md).

## How the launcher runs your app

APPLaunch launches the `Exec`, tracks whether the child keeps elevated rights, and — crucially —
**shares the keyboard input device with the child** (no exclusive grab), so your app reads the same
evdev device the launcher does. For a `sudo -n` app it runs non-interactively; if the sudoers rule
isn't present, it fails fast.

## Reaching the hardware

How the device's own hardware apps behave — the patterns to reuse:

- **Acquire on enter, release on exit.** On open, power the peripheral and claim its lines; on close,
  **restore them to how you found them** (including pins shared with the display bus). Leaving state
  clean is part of not breaking the next app.
- **Power rails and routing** are controlled via `/sys/class/leds/…` (e.g. an `ext_5v_out`
  brightness of 255 = on, 0 = off) plus the relevant GPIO.
- **GPIO** via `libgpiod` on `/dev/gpiochip0`; **SPI** via `/dev/spidevX.Y` (the kernel handles
  chip-select); **serial** via `/dev/ttyS0` (check the serial-console getty is disabled first);
  **I²C** via `/dev/i2c-N`. All usable unprivileged thanks to group membership.
- **Display:** LVGL on the framebuffer, fixed 320×170.
- **Keyboard:** read the shared evdev keyboard device the launcher hands you.
- **Audio:** PipeWire runs in the *user* session. A root-elevated app must point at it explicitly
  (set `XDG_RUNTIME_DIR` and `PULSE_SERVER=unix:$XDG_RUNTIME_DIR/pulse/native`) or sound won't reach
  the speaker.
- **Logging:** log structured lines to the journal (`journalctl`). It's how you'll debug everything.

## Ship your licenses *in the package*

Even tiny built-in apps ship, under `/usr/share/doc/<pkg>/`, a **`LICENSE`** and a
**`THIRD_PARTY_NOTICES.md`** that names each borrowed component with its source URL, exact reference
commit, and full license text. This is the trust signal that tells a user your app is honest about
what it's made of. Match it. The full attribution bar is in
[security and publishing](08-security-and-publishing.md).

---

Next: the one architectural decision that shapes everything else —
[an architecture that works](03-architecture.md).
