# Network clients and services

First decide which peers may communicate and what they may do. A local private
helper, a cloud API client and an intentionally remote server need different
network policies. Do not impose Mesh's private-daemon firewall design on every app.

## Clients and background jobs

Use authenticated encrypted connections where appropriate, validate certificates,
bound messages/queues/time and keep retries cancellable. Store user credentials
privately at runtime; never put them in examples, packages, logs or screenshots.
Keep a reconnect from replaying a consequential action without an explicit policy.
Document offline behavior and preserve recoverable edits on network failure.

## Private local helpers

Prefer binding only the required local interface. If an owned dependency cannot
bind privately, establish and verify narrow confinement before it starts. Check
its separately installed service/autostart behavior and keep unrelated firewall
rules intact. Restrict Unix sockets to an owned private directory, authenticate
peer credentials and define the same-user trust boundary. Use bounded framing,
request correlation and partial-write failure handling from the common security
chapter. These controls do not turn an unauthenticated API into a remote service.

## Intentionally remote services

Define pairing/authentication, authorization for every action, encrypted transport,
credential revocation and the intended exposure. A routing tunnel or address alone
is not application authorization. Make remote-control targets and results explicit;
never accept arbitrary shell commands as an API. Describe whose infrastructure
and continuous connectivity the feature needs before asking users to configure it.

## Acceptance checks

Test offline/slow/disconnecting peers, malformed/oversized input, invalid credentials,
wrong-target replies and expired operations. For IPv4/IPv6 confinement, establish
a reachable control on the same path/address family; "unreachable" alone proves
nothing about the firewall. Keep isolated namespace tests and physical LAN probes
separate. See [security](../08-security-and-publishing.md) and the [Mesh example](../case-studies/mesh.md).

[Project selector](README.md)
