# 8. Security, licensing and publishing

Publishing an app people carry on a radio-capable device is a trust transaction. Two things earn
that trust: **least privilege** (it only touches what it says it does) and **integrity/provenance**
(they can tell it's really yours and unmodified). This chapter is both — plus the specific hardening
lessons from putting a real app through an independent security review.

## Least privilege

Most of your app should need **no root at all** — the device user is already in the `gpio`/`spi`/
`i2c` groups, so SPI/GPIO/I²C work unprivileged. Escalate only for the few things that truly require
it (raw sockets, monitor mode, firewall rules), and do it narrowly. In order of preference:

1. **File capabilities** (`setcap`) — e.g. `cap_net_raw+eip` on just the binary that needs raw
   sockets. No sudo, no root process.
2. **A scoped, sandboxed `systemd` unit** — its own unit (not a child of your UI), started through a
   narrow policy, with `User=<non-root>` (or `DynamicUser=yes`), `NoNewPrivileges`, an empty
   `CapabilityBoundingSet=`, `ProtectSystem=strict`, `DeviceAllow=` only the device it needs.
3. **A root-owned validating wrapper** — only where capabilities can't reach, and it **re-validates
   every argument.**

The publish tooling enforces the floor: **a bundled service running as root is rejected.** Never ship
a blanket `NOPASSWD: ALL`. And resist the convenience trap of exposing an on-device root shell —
fine for a personal tool, wrong for a trust-first published app. Prefer enumerated, validated
actions.

The single most important rule, from [the architecture chapter](03-architecture.md): **IPC carries
intent, not mechanism.** The unprivileged side sends `{"intent":"radio.start"}`, never a command
string; the privileged side maps that to one fixed, validated action and **treats everything it
receives as untrusted input.**

## Hardening lessons from a real review

These are the things an independent review flagged on a real app — the non-obvious ones worth
building in from the start:

- **Confine any network daemon you spawn to loopback.** A bundled daemon may bind *all* interfaces by
  default (and offer no option to restrict it), quietly exposing a control API to the whole network.
  Pin it to a fixed localhost port and add a firewall rule (nftables/iptables) that drops that port
  on every interface except `lo`. Verify what it actually listens on (`ss -tlnp`) — don't assume.
- **Make your control socket private and verified.** Put the Unix socket in an owner-only (`0700`)
  directory, mode `0600`, and have the client check (via peer credentials) that the server is owned
  by the same user — otherwise, on a predictable `/tmp` path, another local user could impersonate
  your supervisor and receive whatever the UI sends.
- **Bound every input.** Cap line length, JSON nesting depth, queue sizes, and connection counts;
  reject malformed messages. A local peer that sends a huge line, deeply nested JSON, or simply stops
  reading should not be able to exhaust memory or stall your process. Use per-client bounded write
  queues so a slow reader can't block everyone.
- **Don't let your UI die on a broken socket.** Make socket writes SIGPIPE-safe (`MSG_NOSIGNAL`) and
  time-bounded, so a stuck or gone supervisor can't crash or freeze the app.
- **Mean what your settings say.** If a toggle claims to turn something off (location sharing, a
  broadcast), make sure it *actually stops the behavior* — read back the effective state rather than
  trusting that writing a config value did what you expected.
- **Own your processes cleanly.** Serialize start/stop of anything that holds hardware; reap an
  orphaned child from a previous crash on startup; power the hardware down on abnormal exit.

The meta-lesson: **have someone (or something) review it who isn't you**, before you publish. An
author is blind to their own omissions.

## No secrets, ever

- No keys, tokens, passwords, or private channel material in the repo or the `.deb`.
- User secrets (e.g. a radio channel key) live in the **user's config dir at runtime**, created by
  the user — never committed, never baked into the package. Keep the simulator's sample/fixture data
  **wholly synthetic** (no real identities, coordinates, or ids).
- **Scan before every release:** `git grep -iE 'password|secret|token|BEGIN .*PRIVATE KEY'`, and grep
  for your own device name, hostnames, local IPs, and home paths before a repo goes public.

## Licensing (including the MIT/GPL split)

- **Choose and state a license up front**, in the repo and shipped in the package
  (`/usr/share/doc/<pkg>/LICENSE`). Apps derived from the official template inherit **MIT** —
  preserve the upstream copyright.
- **Mind the copyleft.** The Meshtastic stack (`meshtasticd`, the `meshtastic` Python library) is
  **GPL-3.0**. If any of your *code* links a GPL library in-process, that code must be
  GPL-compatible. A clean, real-world split:
  - Your **C++/LVGL UI stays MIT** — it only talks to the other process over a socket (separate
    process, no license entanglement).
  - The **supervisor is GPL-3.0** if (and only if) it imports a GPL library in-process.
  - **Don't redistribute the GPL daemon/library** in your repo or `.deb` — depend on them and have
    the user install them. Then you distribute no GPL binaries, and only the one process that links
    the library is itself GPL.
  - Running a separate GPL *program* as a subprocess (e.g. launching `meshtasticd`) does **not**
    entangle your code — that's a separate process, like a shell invoking a tool.

## Integrity, attribution, and the Store gate

- **Public source repo; build the published binary from it; tag releases**, so a reader can match the
  downloaded `.deb` to a commit.
- There is **no code signature** in this ecosystem. Integrity rests on a **SHA-256** of the `.deb`
  (the Store records and verifies it) plus the public repo. Publish the `.deb` as a GitHub Release
  and list its SHA-256 so anyone can `sha256sum` what they downloaded. **Never** `curl … | sudo bash`
  — ship a `.deb` they can inspect.
- **Ship attribution in the package:** a `LICENSE` and a `THIRD_PARTY_NOTICES.md` naming every
  borrowed component with its source URL, exact reference commit, and full license text. Preserve
  truncated upstream license texts in full.
- **Declare the 7 permission flags truthfully** and state plainly in your README what hardware and
  network your app uses and why. For a radio app, state the safety and legal rules outright.
- **Use the Store's hardware-video review as a forcing function:** if it isn't polished and working on
  the device, it isn't ready.

## Pre-publish checklist

- [ ] Public repo; binary builds from it; release tagged.
- [ ] License chosen and shipped; **GPL vs MIT split correct** if you link a GPL library.
- [ ] `.deb` on a GitHub Release with its **SHA-256** listed.
- [ ] Runs **unprivileged**; any privilege is capabilities or a scoped sandboxed unit, never blanket
      sudo; **no root service.**
- [ ] Any spawned network daemon is **loopback-confined**; the control socket is owner-only and
      ownership-verified; inputs are bounded.
- [ ] No secrets in repo or package (grep clean); user secrets live in the user's config dir; fixtures
      synthetic.
- [ ] `app-builder.json` permissions honest; README states what it touches and (for radio) the
      safety/legal rules.
- [ ] `LICENSE` + `THIRD_PARTY_NOTICES.md` (source + commit + license) shipped in the package.
- [ ] Real icon + real 320×170 screenshots; no `TODO`/placeholder text anywhere.
- [ ] Reviewed by someone who isn't you; verified on the device; ready to record the hardware video.

---

That's the path, end to end. For a complete implementation of everything here, read the
**[worked example](https://github.com/Prophet60191/m5stack-cardputer-zero-mesh-app)**. Build
something good.
