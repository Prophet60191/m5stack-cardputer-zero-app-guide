# Local utilities, notes and simple games

A calculator, timer or local notes tool can begin with one unprivileged process.
Use the [official shell](../components.md), supported keyboard path and ordinary
app settings. A backend process is optional. Keep file indexing or other slow work
on bounded jobs and deliver results on the UI thread.

## Decide the behavior before adding infrastructure

- Keep a calculator's state local; distinguish clear-entry, clear-all and Escape.
- Use a monotonic clock for elapsed timers, and define whether they continue while
  the app is closed. A wall-clock change must not change an elapsed duration.
- For notes, use stable record IDs and deliberate save/recovery behavior. Keep
  draft text on rejected saves; flush at defined close/navigation boundaries.
- For games, distinguish text input from game key identity/repeat. Do not apply
  a navigation shortcut policy to every game key. Budget assets and redraw work.

## Acceptance checks

Exercise every action with the actual input adapter, long/empty text, repeated
keys and overlays. Check focus and selection after deleting/reordering records.
Test full-disk/save failures, restart and malformed settings if data persists.
Measure memory/startup and timer behavior on the target; simulation alone does
not prove frame rate, power use or hardware input.

The optional editor in the [prepared keyboard proposal](../../contributions/template-keyboard/README.md)
is a small integration example without a radio/service. It is not a completed
notes application or evidence that a general library has two production consumers.

[Project selector](README.md)
