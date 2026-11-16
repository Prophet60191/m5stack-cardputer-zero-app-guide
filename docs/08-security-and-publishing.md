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

- **Make network confinement a startup precondition.** If a daemon binds all
  interfaces, choose one fixed port and establish a dedicated IPv4/IPv6 firewall
  rule before spawning it. A command run once is lost on reboot; ship boot
  integration and verify the actual rule before every start. Stop on a failed
  watchdog recheck. Never flush unrelated rules. Use a capability-limited oneshot
  service or another narrow privileged boundary; keep the UI unprivileged.
  A loopback firewall still permits local clients; disclose that trust boundary.
- **Check dependency autostart too.** Installing a daemon package can enable a
  separate system service with a different API port. Mask that service before
  installation when the app must own its child daemon; check for conflicting
  enabled/running units before power-on. A firewall for your child port does not
  confine another instance on its default port.
- **Authenticate and exclusively own the socket.** Use a real, UID-owned 0700
  directory, a 0600 socket and peer-credential checks. Reject symlink directories
  and unexpected owners. Hold a kernel advisory lock before unlinking a socket;
  checking its owner alone does not prevent two instances replacing each other.
- **Bound bytes, allocations, work and time independently.** Limit complete and
  unterminated frames, JSON depth/value/string counts, pending queue bytes and
  records, clients, retained history, active workers and request queues. A count
  limit alone can still retain hundreds of huge messages. Limit UI events per
  tick. Reject malformed UTF-8/JSON and non-finite or overflowing numbers. Validate
  field ranges before arithmetic/drawing; type checks alone are not enough.
- **Treat a partial write as a broken stream.** A timeout can leave a JSON prefix
  in the peer's buffer; sending the next record on that stream corrupts framing.
  Close/reconnect on incomplete writes and report failure; never automatically
  replay radio or destructive actions. Put bounded writes on a worker with an
  absolute deadline, not on the LVGL thread. Suppress SIGPIPE.
- **Show confirmed effective settings.** A click is a request, not proof. Keep
  privacy state Pending/Unknown through disconnects, rejected writes, readback
  failures and timeouts. Confirm against the device, not the library cache you
  just edited. Test the actual behavior of “Off”; an interval of zero may mean
  the firmware default rather than disabled.
- **Validate every route to an RF action.** A DM destination does not bypass
  channel validation. Reject broadcast aliases disguised as destinations. Check
  real key formats and public/private classification, not just a channel name.
  Supporting public channels is compatible with a secure client: use clear labels,
  explicit selection, and separate location opt-in. Enabling location on one
  channel must not also enable another.
  Preserve channel identity through pickers, details, intents and share replies.
- **Own descendants and hardware through abrupt death.** Parent termination does
  not imply child termination or power restoration. Use a guardian/service
  control group, stop/reap the child before restoring switches, and test SIGKILL
  and failed startup. Do not kill arbitrary PIDs matching a config pathname.
- **Make reconnect snapshots true.** Persist delivery changes in the authoritative
  session store, deduplicate retries, ignore stale attempt ACKs, and propagate
  deletion/retention changes to every client. Put a global bound on “keep all.”

The meta-lesson: **have someone (or something) review it who isn't you**, before you publish. An
author is blind to their own omissions.

## No secrets, ever

- No keys, tokens, passwords, or private channel material in the repo or the `.deb`.
- User secrets (e.g. a radio channel key) live in the **user's config dir at runtime**, created by
  the user — never committed, never baked into the package. Keep the simulator's sample/fixture data
  **wholly synthetic** (no real identities, coordinates, or ids).
- **Scan before every release:** `git grep -iE 'password|secret|token|BEGIN .*PRIVATE KEY'`, and grep
  for your own device name, hostnames, local IPs, and home paths before a repo goes public.
  Scan tracked files, reachable Git history, package contents and images. A clean
  text scan does not inspect a screenshot: replace real chats, names, coordinates
  and device IDs with synthetic fixtures. Deliberate public copyright/author
  attribution should remain; it is different from accidentally exposed user data.

## Licensing (including the MIT/GPL split)

- **Choose and state a license up front**, in the repo and shipped in the package
  (`/usr/share/doc/<pkg>/LICENSE`). Apps derived from the official template inherit **MIT** —
  preserve the upstream copyright.
- **Mind the copyleft.** The Meshtastic stack (`meshtasticd`, the `meshtastic` Python library) is
  **GPL-3.0**. If any of your *code* links a GPL library in-process, that code must be
  GPL-compatible. A clean, real-world split:
  - Your **C++/LVGL UI stays MIT** — it only talks to the other process over a socket (separate
    program; preserve the distinct licenses and interfaces).
  - The supervisor incorporates the GPL client library and is licensed **GPL-3.0-or-later**.
  - **This example does not redistribute the GPL daemon/library** in your repo or `.deb` — depend on them and have
    the user install them. Then you distribute no GPL binaries, and only the one process that links
    the library is itself GPL.
  - Running a separate GPL *program* as a subprocess (e.g. launching `meshtasticd`) does **not**
    by itself determine the other program's license; the nature of the integration
    and applicable terms still matter. The example publishes both components as
    open source with explicit licenses.

GPL allows redistribution subject to its terms, including the applicable
source obligations; not bundling a dependency is a distribution choice, not a
GPL prohibition. See the [GPLv3 text, sections 4-6](https://www.gnu.org/licenses/gpl-3.0.html).
Ship the full notices for the libraries and generated font data actually included
in your binary, including components bundled inside LVGL; preserving only your
application's MIT license does not preserve their copyright notices.

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
- [ ] Firewall survives reboot and is verified before daemon startup;
      failed verification prevents power-on. Any network daemon is **loopback-confined**; the control socket is owner-only and
      ownership-verified; inputs are bounded.
- [ ] No secrets in repo or package (grep clean); user secrets live in the user's config dir; fixtures
      synthetic.
- [ ] `app-builder.json` permissions honest; README states what it touches and (for radio) the
      safety/legal rules.
- [ ] `LICENSE` + `THIRD_PARTY_NOTICES.md` (source + commit + license) shipped in the package.
- [ ] Real icon + real 320×170 screenshots; no `TODO`/placeholder text anywhere.
- [ ] Regressions exercise malformed/oversized frames, stalled readers, partial writes,
      parent death, config rejection, wrong-target replies and reconnect snapshots.
- [ ] Inspect the generated `.deb`, not only the source manifest: identity/version,
      native library dependencies, icon/launcher paths, helpers/services and modes.
- [ ] Reviewed by someone who isn't you; verified on the device; ready to record the hardware video.

---

That's the path, end to end. For the implementation and its explicit verification limits, read the
**[worked example](https://github.com/Prophet60191/m5stack-cardputer-zero-mesh-app)**. Build
something good.


For port-confinement tests, verify a control endpoint is reachable on the same
address family/path. “Network unreachable” is not evidence of a firewall drop.
When the physical LAN cannot route IPv6, isolated network namespaces can verify
the device kernel's IPv6 filtering; report that separately from a physical LAN
probe, and leave the untested path explicit.

## Useful diagnostics without an accidental data export

Build support exports from a small whitelist of health states, versions, ages and
counts. Exclude raw logs, names, node/device identities, keys, share URLs, coordinates,
message text and personal paths. Test the export with synthetic sensitive sentinel
values and verify they cannot appear. A generic recursive redactor applied to a
raw runtime dump is harder to reason about than selecting known safe fields.

Conversation history and named hardware profiles introduce new sensitive files.
Use private owned directories/files, bound history and record counts, define
retention and deletion behavior, and offer an explicit RAM-only choice. Describe
logical deletion honestly: flash, WAL and backups may retain old bytes, and private
permissions are not at-rest encryption. Never put runtime state into CI artifacts.

History opt-out must cover metadata as well as message/draft text: conversation
identifiers and pins can reveal contacts. Suppress new metadata writes, migrate
older opted-out stores, and test raw rows after restarting. Retaining that state
in the active RAM session is a separate, explicit policy.

When a privilege design changes, remove obsolete sudo grants from the package
and verify their absence after a real upgrade. A documented manual diagnostic
command is still a privilege grant; replace it with an unprivileged health read
when a trusted capability-only monitor already supplies the needed evidence.

Keep strict validation ahead of idempotence checks. In Python, `True == 1`, so an
unchanged-state shortcut can accidentally accept an invalid flag. Once validated,
skip duplicate persistence/broadcasts while retaining durability for real changes,
history opt-out semantics, row quotas and explicit synchronization barriers.

Uninstallation needs an audit of changes made outside the package manifest:
generated services, setuid helpers, file capabilities, runtime data and installer
caches. A capability applied through a virtualenv symlink can land on the shared
system interpreter. Prefer narrow service capabilities; avoid elevating a shared
interpreter. Back up private app data, remove only grants actually attributable
to that app, and preserve shared dependencies, hardware configuration and groups
needed by other applications.
