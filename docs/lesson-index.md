# Where the lessons live

The guide is now organized around a common foundation and optional project types.
The detailed source paragraphs moved from chapters 3/4 and the radio/licensing
examples in chapter 8 are preserved in the [Mesh case study](case-studies/mesh.md).
A one-time block-by-block audit checked all 30 moved lesson blocks against
[the previous guide revision](https://github.com/Prophet60191/m5stack-cardputer-zero-app-guide/tree/a7ddc7ff73e71a32c71b68bbc87290af73424eea).
General chapters retain their existing paths and forwarding headings where needed.

| Lesson learned | General rule / optional detail |
|---|---|
| Guardian, ownership lock, service lifecycle and abrupt death | [Architecture](03-architecture.md#why-a-separate-supervisor), [hardware](projects/hardware.md), [Mesh evidence](case-studies/mesh.md) |
| Bounded JSON, partial writes, socket ownership and callback identity | [Security](08-security-and-publishing.md#hardening-lessons-from-a-real-review), [networking](projects/networking.md) |
| Stable channel identity, drafts, history, retries and ACK source | [Stable identity](03-architecture.md#preserve-identity-and-durable-intent-safely), [messaging](projects/messaging.md), [original details](case-studies/mesh.md#architecture-and-state) |
| Pending/Unknown state, overlay lifetimes and deadlines | [UI ownership](04-ui-and-polish.md#privacy-state-and-asynchronous-overlays), [original details](case-studies/mesh.md#ui-and-asynchronous-operations) |
| First run, receive-only, transmitter/location consent and profiles | [General setup](04-ui-and-polish.md#first-run-and-uncertain-live-data), [LoRa](07-radio-bring-up.md), [hardware](projects/hardware.md) |
| GPS validity, freshness and receiver versus sharing | [GPS/maps](projects/gps-and-maps.md) |
| Actual camera stack, Return starts scan, busy feedback, preview/commit and cancellation | [Camera/QR](projects/camera-and-qr.md), [original details](case-studies/mesh.md#ui-and-asynchronous-operations) |
| Debounced saves, independent workers, stable selection and measured optimization | [UI persistence/performance](04-ui-and-polish.md#persistence-and-redraws), [Mesh measurements](https://github.com/Prophet60191/m5stack-cardputer-zero-mesh-app/blob/c51a45ee61813bf9685766f9f45c95e6778780a5/docs/maintenance-pass.md) |
| Fixed context/help lanes, inside borders, settings groups and stable actions | [UI layout](04-ui-and-polish.md#keep-context-and-keyboard-help-readable), [original details](case-studies/mesh.md#ui-and-asynchronous-operations) |
| Correct official Sym/Fn map, per-device state and real event-path tests | [Keyboard](05-keyboard.md), [focused contribution](../contributions/template-keyboard/README.md) |
| Retention toast on startup/reconnect | [Quiet synchronization](04-ui-and-polish.md#show-whats-happening) |
| Private data, metadata opt-out, diagnostics whitelist and uninstall cleanup | [Security and diagnostics](08-security-and-publishing.md#useful-diagnostics-without-an-accidental-data-export), [messaging](projects/messaging.md) |
| MIT/GPL distribution choices and complete notices | [General licensing](08-security-and-publishing.md#licensing-including-the-mitgpl-split), [actual Mesh choice](case-studies/mesh.md#licensing-choices-in-this-application) |
| arm64 package CI, exact running-code verification and installed privileges | [Build/install checks](06-building-and-packaging.md), [Store checklist](store-readiness.md) |
| Store policy pins, permissions, accepted paths and non-publishing checks | [Store readiness](store-readiness.md), [preflight](../tools/README.md) |

For historical discussions or full earlier wording, use Git history. For an
implementation claim, follow the pinned app evidence rather than assuming a
lesson's presence in this guide means it is implemented/tested in a new project.

[Guide index](../README.md)
