# 7. Radio bring-up (LoRa Cap)

*Only relevant if your app drives the Cap LoRa-1262.* This is the sequence to power and initialize
its SX1262 **robustly** from userspace with no root. Getting it wrong is what defeated earlier
attempts on this device, so it's worth doing carefully.

> ⚠️ **Attach the antenna before powering the radio.** Transmitting without an antenna can
> permanently damage the SX1262. The software cannot check this — it's on the user, so say so in your
> UI and docs.

## Confirmed wiring (this Cap on this board)

| Line | Value |
|---|---|
| SPI | `/dev/spidev0.1` (kernel CS1) |
| RESET | GPIO26 |
| BUSY | GPIO22 |
| DIO1 / IRQ | GPIO23 |
| RF switch | SX1262 **DIO2** (`DIO2_AS_RF_SWITCH=true`) |
| TCXO | SX1262 **DIO3**, 3.0 V |
| Cap 5 V rail | `/sys/class/leds/ext_5v_out/brightness` (1 = on) |
| EXT selector | `/sys/class/leds/ext_usb_gpio_fun/brightness` — **must be 0** (GPIO mode) |
| Band-path expander | **PI4IOE5V6408 at I²C `0x43` on `/dev/i2c-1`** (lives *on the Cap*; only answers once the 5 V rail is up) |
| GNSS | `/dev/serial0` @ 115200 (shares the 5 V rail) |

## Run it in a child process

Run the radio in a **child process whose lifetime matches the connection**, so the kernel frees every
GPIO line and the spidev handle the instant it exits or crashes — no stuck pins, no lingering lock.
**Let the kernel be the lock:** don't invent a lockfile for the SPI bus; a second claimant gets
`EBUSY` and the kernel cleans up on exit. (This is the same child-process boundary the
[architecture chapter](03-architecture.md) recommends for all hardware work.)

## The sequence (ordered)

1. **Pre-flight.** Check `/dev/spidev0.1`, `/dev/gpiochip0`, `/dev/i2c-1` exist and are read/write;
   turn each failure into a specific message (`no-spi` / `no-gpio` / `no-i2c` / `permission` → "add
   your user to the `spi`, `gpio`, `i2c` groups and re-login"). If a known holder owns the radio
   (another LoRa app, a bridge), say so rather than retry-failing.
2. **Power, saving state first.** Read and **save** the current `ext_5v_out` and `ext_usb_gpio_fun`
   values. Write `ext_5v_out=1`, then `ext_usb_gpio_fun=0` (at `=1` the Cap's reset line is cut and
   the chip stays in reset). **Sleep ~100 ms** for the regulator and the on-Cap expander to come up.
3. **Band path (the 0x43 expander).** On `/dev/i2c-1`, address `0x43`: verify the ID register first
   (expect `0xA2`, maker bits `0b101`); then write the **output level (reg 0x05) before the direction
   (reg 0x03)** so the RF-enable pin comes up already-high with no low glitch, then high-Z
   (reg 0x07). Classify every failure (`busy` / `absent` / wrong-chip) with an actionable message; on
   any failure here, **restore the LED switches** and abort cleanly.
4. **Init the SX1262.** Let your radio library do the reset pulse, BUSY handshake, DIO3-TCXO (3.0 V),
   DIO2-as-RF-switch, and image calibration — don't hand-code them. Construct with: SPI `spidev0.1`,
   RESET 26, BUSY 22, IRQ/DIO1 23, `DIO2_AS_RF_SWITCH=true`, `DIO3_TCXO_VOLTAGE=3.0`. **Filter
   constructor kwargs against the driver's real signature** so a library version that doesn't accept
   a field doesn't crash you. `begin()` with **a few retries and escalating backoff** (~1.5 s) to
   ride out a line a dying prior process is still releasing.
5. **Serve / run.** This is where your actual radio work happens — e.g. running `meshtasticd` against
   the now-powered Cap, which handles the SX1262 and the Meshtastic protocol via its YAML. The **Cap
   power + the 0x43 band path are yours to do first**, because the radio daemon does not drive them.
6. **Teardown, guaranteed.** In a `try/finally`: stop the radio, then **restore `ext_usb_gpio_fun`
   and `ext_5v_out` to their saved values in reverse order** (5 V rail back off, so the Cap doesn't
   drain the battery). This must run even on a failed start or a crash.

## Gotchas (each one cost real debugging)

- `ext_usb_gpio_fun` **must be 0**, or the Cap's reset line is cut and the SX1262 stays in reset.
- Power the rail and **settle ~100 ms before** touching the expander — it has no power before that,
  so probing it earlier reads a false "absent."
- Write the expander's **output level before its direction** to avoid a low glitch on the RF-enable
  pin.
- The radio library's IRQ-watch thread can stall shutdown ~2 s, but the launcher only allows ~3 s
  between SIGTERM and SIGKILL — stop the edge threads before cleanup or your app looks like it hangs
  on quit.
- Resolve the gpiochip by its kernel **label, not its number** — the number can move across CM
  revisions and kernels.

## If you bundle a GPL radio daemon

`meshtasticd` and the `meshtastic` Python client library are **GPL-3.0**. If your supervisor imports
the library in-process, that process is a derivative work and must be GPL-compatible (your C++ UI, a
separate process talking over a socket, is not). The clean split: **don't bundle the GPL daemon or
library in your repo** — depend on them and have the user install them — and license the one process
that *links* the GPL library as GPL-3.0 while your UI stays whatever you choose. See
[security and publishing](08-security-and-publishing.md).

## Legal/operational rules to surface in your app

- Use a band you're **licensed** to transmit on (e.g. 902–928 MHz in the US).
- **Antenna before power** (above).
- Use **your own private channel**, not the public default, for your own traffic.

---

Next: shipping it safely — [security and publishing](08-security-and-publishing.md).
