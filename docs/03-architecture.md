# 3. An architecture that works

Choose the simplest design that keeps this app responsive, testable and within
its privilege and memory budget. The UI/backend split used by Mesh is one option.
Start from the [official component comparison](components.md) before inventing a
second platform layer. No app is required to depend on Python, a radio, a socket
or a permanently running service.

## Choose the amount of machinery the app needs

| App behavior | Suitable starting point | What to verify |
|---|---|---|
| Calculator, timer, small local utility | One normal user process with screen state and bounded callbacks | Navigation, timing, close/reopen and memory use |
| Notes, file indexing, network requests | One UI process plus bounded worker jobs, or an existing compatible official service | UI-thread delivery, cancellation, timeouts, safe saves and shutdown |
| Hardware ownership that must outlive the UI, a child daemon, or a privilege boundary | Separate service/supervisor with an explicit protocol | Ownership, authentication, process cleanup, hardware restoration and reconnect state |

A thread can keep a slow task off the UI; it does not create a privilege boundary.
A process boundary helps only when its permissions, protocol and ownership are
actually enforced. Do not add a background daemon to an otherwise local utility
just to match a worked example.

## Why native LVGL for the UI

The official C++/LVGL Template is a useful starting point for native-looking apps
with a desktop simulator. Its MVVM helpers and standard widgets reduce repeated
UI plumbing. Other stacks are valid when they meet the launcher/input contract,
fit the target image and deliver acceptable interaction, memory use and startup.

Choose a language/toolkit for the app's needs and available libraries. Measure
startup, resident memory and input response on the supported device. Avoid broad
claims that all Python interfaces are slow or that a toolkit name guarantees a
polished interface. [Build and packaging](06-building-and-packaging.md) covers the
native recipe and Python dependency choices; [project sections](projects/README.md)
identify additional work for media, hardware or networking.

## Why a separate supervisor

Use this option when a resource needs independent lifetime, explicit ownership,
child-process containment or narrowly different privileges. The UI presents state;
the owner performs validated actions and reports authoritative results. This can
be C++, Python or another suitable implementation. It normally remains unprivileged.

```text
UI (LVGL thread) -> validated request -> resource owner -> device / job / daemon
UI (LVGL thread) <- bounded result    <- resource owner
```

The UI can use a fake owner in desktop tests. Establish the simulator boundary
before acquiring actual hardware. Keep the owner independent of screen rebuilds.
Hold a lifetime ownership lock before replacing sockets or recovering resources.
A stale PID file or broad process-name kill is not an ownership mechanism.

Kernel exit releases descriptors and GPIO requests, but does not restore sysfs
power/mux values or necessarily kill detached descendants. If the app changes those
resources, design stop/reap/restore ordering and recovery for abrupt death. A
`finally` block cannot handle SIGKILL. A guardian or a correctly scoped service
control group may be appropriate; test real subprocesses against fake hardware
before making device claims. None of this requires adding a guardian to an app
that owns no such resources. See [hardware projects](projects/hardware.md).

## Intents, not mechanism

If processes communicate, define named actions such as `job.start {record_id}` and
`job.cancel {request_id}`. Validate action names, types, ranges, authorization and
target identity at the resource owner. Never interpret a received command string
as a shell command. Paths and URLs, if part of the app's purpose, need an explicit
allowlist/sandbox or destination policy rather than blind interpolation.

A private Unix socket with bounded newline-delimited JSON is one implementation,
not a universal requirement. Authenticate clients, limit frames/queues/work/time,
correlate replies and define reconnect/error semantics. Workers must marshal
results onto the UI thread; they must not retain or mutate LVGL objects after the
view has gone away. See [security](08-security-and-publishing.md).

## The MVVM shape of the UI

When using the official Template, keep application state in its model/viewmodel
and connect LVGL subjects to views with bindings. The screen manager owns screen
switches; each screen and widget owns its observers, timers and LVGL objects.
Keep those lifetimes explicit. Other UI stacks need an equivalent separation of
state, presentation and resource ownership, rather than these exact C++ classes.

## Separate the device facts from the app logic

Keep display/input capabilities and board wiring in a small platform adapter.
Resolve a supported board/image once and inject an interface that can be faked.
Do not apply one Cap's GPIO/I2C/power values to every peripheral. Identify GPIO
controllers by their documented labels where numbering can change. A presence
probe must itself respect the peripheral's safe power sequence.

Use the official foundation when it fits. Adapt a small component for a documented
gap and carry its tests/provenance with it. Require reuse in a second unrelated
app and a maintenance plan before creating a general library. See the
[component decisions](components.md).

## Make the boundary authoritative

Keep committed state at its real owner. A successful button press is not proof of
a completed write; reconnect snapshots must reflect confirmed results. Associate
asynchronous work with a request ID and a stable target ID, not a vector index or
pointer. Ignore late results after a view is dismissed, while still reporting any
operation that actually committed. Define which client wins conflicting preferences.

## Preserve identity and durable intent safely

An index or slot is a location, not an identity. Resolve stable identities again
before accepting delayed work. Validate before equality/idempotence shortcuts:
values such as Python `True` and `1` compare equal despite different types.
For secret-bearing records, avoid exposing raw secrets or guessable plain hashes
as identity. Use a suitable local keyed digest where that is the chosen design.

Commit related persistent changes consistently and recover interrupted writes.
Coalesce repeated state, but retain durability barriers and request completion.
Register callbacks with the actual event library used in production and test its
parent/child subscription contract. Keep slow dependency probes outside lifecycle
locks; guard shared references and distinguish cached version information from a
fresh security/compatibility verdict.

Messaging delivery stages, conversation archives, retries and saved radio profiles
are detailed in [messaging projects](projects/messaging.md) and the preserved
[Mesh lessons](case-studies/mesh.md#architecture-and-state).

Next: [UI and polish](04-ui-and-polish.md).


## A documented modularity decision

Mesh's [architecture decision](https://github.com/Prophet60191/m5stack-cardputer-zero-mesh-app/blob/f1c2c77b9ccb1a26ff366539af7d51f371a3e8af/docs/architecture.md)
explains its native UI/Python owner choice: an existing client library, background
reception after UI exit, explicit resource authority and independent tests. It
also records extra resource/protocol/upgrade costs, same-user trust and hardware
recovery limits. Describe the purpose, goal and verified benefits of a split in
your own app; do not treat the word modular as automatic safety, reusable-library
readiness or a reason every application needs a service.

## Worker construction and durable measurement jobs

Start a worker thread in the constructor body after all mutexes, condition
variables, settings and queues have been initialized. C++ initializes members
in declaration order; starting a thread in an earlier member initializer can
expose later members before their construction. Stress/sanitizer passes alone
do not prove that race absent. Cancellation/reset handoff needs one owner/lock,
and views should receive owned data with generation/request identities.

When a batch is persisted, validate the exact collection being written and
advance duplicate-suppression state only after its transaction commits. A failed
write must permit the same acquisition token to be retried. Heavy report jobs
should use a real read-only, consistent database snapshot and bounded inputs;
opening a report reader must not run writer recovery or interrupt recording.
Wireless Surveyor exercised these patterns in core, worker and UI regressions.
