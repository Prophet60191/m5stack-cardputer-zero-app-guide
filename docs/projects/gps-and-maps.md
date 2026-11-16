# GPS receivers and maps

Represent location as a measurement, with validity, age, source and quality when
available. A timestamp by itself is not a fix. Validate finite values, coordinate
bounds and clock plausibility at the owner; show stale data as last known rather
than live. Make unknown/missing coordinates explicit in the data model.

Enabling a receiver and consenting to publish location are separate choices.
A map may display a location locally without authorizing network or radio sharing.
Choose a precision policy appropriate for the app and explain any rounding.

Coalesce telemetry, update age labels and bound the number of plotted records.
Document offline map/assets behavior and missing-position states. Resolve GPS
serial ports and power ownership through the supported board/Cap profile; do not
copy the LoRa Cap's shared rail/port assumptions to an unrelated receiver.

## Acceptance checks

Use synthetic valid, stale, absent, future, malformed and out-of-range fixes.
Test clock changes, reconnect and receiver enable/disable independently of sharing.
Then qualify an actual clear-sky fix with the intended antenna, board/image and
receiver. Indoor timestamps, simulated coordinates and parser tests are separate
evidence. The Mesh example's outdoor-fix check remains unqualified; reorganizing
the guide does not close that gap.

See the preserved [Mesh UI examples](../case-studies/mesh.md#ui-and-asynchronous-operations)
and the [LoRa Cap-specific hardware](../07-radio-bring-up.md) where applicable.

[Project selector](README.md)
