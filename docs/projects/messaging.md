# Persistent text, records and messaging

The [common UI rules](../04-ui-and-polish.md) cover responsive editing and stable
selection. Add a durable record model when text must survive closing the app.
A conversation/message model is needed only for a communications app.

## Persistence and identity

Use stable record IDs, bound total bytes/records and make the real state owner
responsible for committed saves/deletions. Keep draft-only, pinned and cleared
records reachable independently of received content. Do not use vector positions
as identities across callbacks or configuration changes.

Define RAM-only versus disk history, what re-enabling storage saves, and deletion
semantics. Metadata such as record/contact identifiers and pins can be sensitive
even without message text. Test raw persisted rows after opt-out/restart. Private
permissions are not encryption and logical deletion does not erase every flash,
WAL or backup copy. See [security](../08-security-and-publishing.md).

## Transport-specific results

Define each transport stage honestly: queued, accepted by a local API, transmitted,
acknowledged by a relay/recipient, failed or unknown. A transport ACK is not a read
receipt. Match replies to a stable message and a particular attempt; ignore stale
ACKs and validate their source. Preserve confirmed results through reconnects.
Never automatically replay an uncertain or failed send after restart.

For Mesh, changing channel keys/names can change a routing identity. Archive the
old context instead of silently sending its drafts to a replacement channel.
A DM draft belongs to both its peer and selected channel. Those rules must be
adapted explicitly for a different transport rather than inheriting LoRa fields.

## Acceptance checks

Cover interrupted saves/sends, delayed and wrong-source replies, retries, reconnect
snapshots, cap reductions, multiple clients and storage re-enable with existing
RAM drafts followed by immediate restart. Check quiet hours across midnight only
if notifications exist. [Detailed Mesh lessons](../case-studies/mesh.md#architecture-and-state)
retain the concrete failure cases and acknowledgment distinctions.

[Project selector](README.md)
