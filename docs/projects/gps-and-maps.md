# GPS receivers and maps

This section helps any CardputerZero app consume GPS reliably: a map, survey
logger, tracker or local instrument. It complements the official hardware and
app guidance. It does not introduce a GPS framework, require Mesh's supervisor,
or replace M5Stack's receiver support. USB receiver work remains unqualified in
my apps; the source-selection guidance below is a design checklist.

## Start with what M5Stack already provides

Reviewed 2026-11-23. Use the [official Zero usage guide](https://docs.m5stack.com/en/compute/cardputerzero/usage)
for the built-in GPS app and [Cap specification](https://docs.m5stack.com/en/cap/Cap_LoRa-1262)
for wiring, supply, UART, antenna and power-off-before-removal precautions.
Do not substitute ESP32 Cardputer/ADV GPIO examples for Zero's Linux device paths.
For this fitted receiver, GNSS is on the Cap; it is not evidence of GPS in a bare Zero.

The [official GPS app](https://github.com/CardputerZero/Cap-LoRa-1262-GPS/tree/f69d99a183a53dd822cebad53692ad94b1d06786)
already offers useful implementation patterns:

| Official source | What to reuse or evaluate |
|---|---|
| `src/gps/linux_serial_backend.cpp` | Console conflict check, nonblocking reads, advisory lock plus exclusive-open request, restoration and cleanup |
| `src/gps/nmea_decoder.cpp` | Bounded sentence assembly/checksum handling and per-field validity |
| `src/models/gps_model.cpp`, `tests/gps_model_test.cpp` | Separate data/fix ages, no-data/search/fix/stale/error states, bounded work and retry tests |
| `src/views/details_panel.cpp` | Receiver/data diagnostics instead of an unexplained empty map |

**Decision:** reuse or adapt the official direct-receiver model when it fits.
When another service owns the receiver, consume that service's supported API;
do not start a second raw reader just to reuse a serial example. Keep the app's
chosen official shell, lifecycle and resource contracts.

The official GPS README describes root/sudo packaging for its preinstalled
power-control path. That is **not** a third-party Store exemption: the current
[development rules](https://github.com/CardputerZero/cardputerzero.github.io/blob/5d5123ca05bfc23e5a920f4e9fdbfaf12685e3ab/docs/en/CP0_dev.md)
prohibit apps running as root. Adapt privilege/resource integration rather than
copying that packaging into a Store app. See [hardware ownership](hardware.md).

<a id="what-our-experience-adds"></a>

## What my experience adds

The reviewed official usage/specification pages explain hardware and operation;
the source already covers many parser, age and ownership concerns. The following
is additional application-integration and qualification guidance, not a claim
that these topics are absent from every M5Stack document or that its GPS app is
broken. Reviewed sources/hashes are in [the evidence record](../gps-official-review-evidence.json).

### Prove each layer separately

A working receiver does not prove a working application. Follow the actual path:

**Receiver -> resource owner -> exported API -> client cache -> UI/map.**

| Layer | Evidence to seek |
|---|---|
| Receiver | Recent valid fixes from the receiver; counts/checksums can prove activity without saving coordinates |
| Resource owner | The owning process has accepted the fix and has the correct power/port/profile |
| API | The supported response really exports the current fix and the fields the app needs |
| Client | A cache receives newer measurements, including loss-of-fix, after connect/reconnect |
| UI | The actual screen shows the fix, its source and truthful age/last-known state |

If raw fixes exist but a map is empty, investigate the boundaries above before
changing receiver firmware, baud rate, antenna or sharing settings. A client
method named “get current position” may only return a cache. Repeated reads of
that cache cannot produce an update that the service never exported.

Use documented stream/snapshot support. Bound refresh frequency, outstanding
requests, completion deadlines and retry backoff. Correlate replies with the
current connection/source generation so an old reply cannot update a replacement
receiver. Do not clear unrelated client state or open a competing connection to
force a refresh. Neither a successful API reply nor new bytes proves a new fix.

### Preserve measurement time and missing fields

Represent validity, acquisition time/age and source explicitly. Keep transport
receipt time separate: receiving the same cached fix again must not reset its
age. Use a local monotonic clock for elapsed deadlines; handle source UTC changes,
unknown time and implausible future timestamps separately. A monotonic timestamp
from another boot/device is not directly comparable to your current clock.

Choose stale thresholds for the receiver cadence, transport delay and action's
risk. The official live viewer uses a different age policy from Mesh's cached
map; neither value is a universal GPS rule. A valid old position may be shown as
**last known**, while navigation, geofence actions or sending may need a fresh fix.
Do not silently repeat an old location as a new measurement.

Validate finite coordinates and geographic bounds. Missing coordinates should
be explicit, not invented at `(0, 0)`; that coordinate is itself a real place
and needs a validity flag to interpret correctly. Distinguish satellites visible,
satellites used and a valid fix. An API that omits satellite count should show
**unknown**, not zero or a count copied from a different diagnostic/source.
Expose altitude, quality/accuracy and constellation details only when supported.

### Treat startup commands as state changes

Identify the exact receiver, owner/library version and protocol before choosing
a workaround. An apparently simple discovery routine may first suppress normal
output. A too-short identification timeout can then leave an enabled receiver
silent. Measure repeated reply latency and command side effects, including the
receiver's output schedule, before changing a deadline.

Separate power/port initialization, model identification and satellite acquisition
timeouts. Increasing one is not a cure for another. Every wait still needs a
bound, cancellation and useful retry/error state. Check whether an attempt changed
receiver output and how normal operation is recovered. Do not hide failures with
endless reset loops, silently flash firmware or persistently change baud/rate/
constellation settings as an unproven repair.

### Keep diagnostics exclusive and location private

There should be one physical resource owner. Access through its API during normal
operation. For a raw diagnostic, stop that owner normally, acquire the supported
hardware/port lease, run a bounded reader, then restore the prior settings and
owner. The official lock/exclusive-open pattern is useful, but do not assume
unrelated programs all cooperate with an advisory lock. Never launch a separate
GPS viewer while a radio service owns the same UART.

Receiver enablement is separate from permission to record, transmit or upload
location. A local map must work with sharing Off. Check this explicitly. A Cap
may share power/resources with other hardware, so retain its documented safety
requirements even when the app only wants GPS; do not generalize a rail or pinout
to other receivers.

For support logs, prefer fix booleans, age, model, error category, latency and
sentence/checksum counts. Raw NMEA, coordinates, track files, screenshots and USB
serial identities can reveal a home or route. Redact or omit them from public
issues and videos; obtain permission before any purposeful location export.

## Choosing internal or external sources

Specify source selection before implementing USB support: manual selection or a
stated priority; what happens on unplug; when fallback is allowed; how stale fixes
are labeled; and whether the user's choice survives restart. Show the active
source. Reconnecting a new receiver must not relabel the previous receiver's
cached position as its fresh fix.

Use supported discovery/stable identity where available, not an assumption that
`/dev/ttyUSB0` always names the same device. Check driver/interface, permissions,
protocol, speed and power needs. Keep identifying serial numbers private. An
external antenna is not automatically a new GPS receiver. USB switching can also
remove the maintenance connection; plan network access independently.

These are design requirements, not a claim that the deferred USB dongle is supported,
automatically preferred, or physically tested.

## Acceptance checks

1. Test synthetic valid, invalid, absent, stale, future, malformed and out-of-range
   measurements, including per-field omissions and repeated cached fixes.
2. Test partial/oversized/bad-checksum input through the selected parser when
   consuming raw data. Reuse official tests/components where suitable.
3. Test receiver enable/disable independently of sharing. Check one resource
   owner and no location emission when sharing is Off.
4. Exercise API timeout, reconnect, late replies, source replacement and clock
   changes. Confirm no fabricated freshness or loss of unrelated app state.
5. Use the actual intended receiver outdoors with a clear sky view and safe
   hardware setup. First acquisition time depends on conditions; a five-minute
   timeout alone does not prove defective hardware.
6. Observe successive acquisition timestamps across a steady interval, not just
   one coordinate. Check the real map/display and loss/stale/recovery states.
7. Repeat starts and error/retry paths. Treat normal receiver restarts, a cold
   whole-device boot and long-term field use as different tests.
8. Record exact app/dependency/package versions, elapsed time and reduced results.
   Preserve settings/data, restore intended operating mode and retain rollback.

Mesh's [qualification record](https://github.com/Prophet60191/m5stack-cardputer-zero-mesh-app/blob/cd82b8ce24a1cab1ef68369e744a508c4ac887ef/docs/internal-gps-validation.md)
now includes actual raw receiver fixes, a local-cache correction, owner-confirmed
Map marker, eight receiver starts and a final 31-sample/321.5-second outdoor watch.
These bounded results supersede the old “outdoor unqualified” note here; they do
not qualify every future app, a USB receiver or unlimited reliability.

The [Mesh case study](../case-studies/mesh.md#subsequent-gps-integration-qualification)
keeps its reserved API nonce, refresh interval and Meshtastic identification
patch separate from this general recipe. Do not copy those settings into an
unrelated receiver or call the Meshtastic defect an M5Stack firmware defect.

[Project selector](README.md) · [Hardware ownership](hardware.md) · [LoRa-specific bring-up](../07-radio-bring-up.md)
