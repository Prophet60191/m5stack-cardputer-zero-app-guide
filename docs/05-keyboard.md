# 5. The keyboard

Input is keyboard-only, and the 46-key keyboard has some sharp edges that *will* cost you debugging
time if you don't know them up front. This chapter is the layout, the modifiers, and — most
importantly — the keycode reality your app has to handle to accept real text.

## The layout

46 keys, **no dedicated arrow keys**. Movement and symbols come from three modifiers:

- **Shift** → uppercase (and the standard shifted punctuation).
- **Fn** → the "orange" shortcuts: arrows, function keys, media, etc.
- **Sym** → the "blue" symbols printed on the keys (`?`, `!`, `@`, `#`, …).

Each modifier works three ways: **hold** it while pressing a key; **tap once** to apply it to the
next key only (sticky); **tap twice** to lock it on.

### Movement (Fn layer)

| Keys | Action |
|---|---|
| Fn + F / X / Z / C | Up / Down / Left / Right |
| Fn + K / N | Home / End |
| Fn + L / M | PageUp / PageDown |
| Fn + Backspace | Delete |
| Hold Esc | Back to the home screen |

Function keys are `Fn + 1…0` (F1–F10), `Fn + O / P` (F11/F12). Useful ones: `Fn + H` (app help),
`Fn + J` (screenshot). So **`Fn + F / X / Z / C` is your d-pad** — that's the arrow cluster your UI
navigates with.

## How the kernel presents keys (and the gotchas)

This is the part to get right. The keyboard driver emits Linux evdev keycodes, but **not** always the
ones you'd expect, and the three modifiers behave differently from one another:

### Fn is translated by the kernel

The kernel keymap turns the **Fn** chords into real arrow/function keycodes. So `Fn + F` arrives at
your app as `KEY_UP`, `Fn + X` as `KEY_DOWN`, and so on — you handle `KEY_UP`/`KEY_DOWN`/`KEY_LEFT`/
`KEY_RIGHT` normally and the Fn layer "just works." (The Fn key itself also shows up as its own
modifier keycode, which you can ignore.)

### Shift you track yourself

Shift arrives as `KEY_LEFTSHIFT`/`KEY_RIGHTSHIFT`. Track it as held/released and use it to pick
uppercase and the shifted punctuation for the number row (`!@#$%…`) and the punctuation keys — the
normal US-layout mapping.

### Sym is **not** translated — and this is the trap

The **Sym** layer (the blue symbols) is *not* turned into ASCII by the kernel. Instead:

1. Sym arrives as **its own modifier keycode** (observed as **383** on current firmware) — you must
   track it as held, exactly like Shift.
2. While Sym is held, each symbol key sends a **device-specific keycode** for its blue symbol — and
   **several of those keycodes collide with ordinary punctuation keys.** For example, the `!` key
   under Sym emits the *same* keycode as the `[` key (`KEY_LEFTBRACE`, 26). Others emit placeholder
   keycodes (e.g. `?` emits 93) that don't map to anything standard.

The practical consequence: if your input layer only tracks Shift (the obvious thing), **the entire
Sym layer silently does nothing** — the user can't type `?`, `!`, `@`, and friends — and if you try
to map the colliding keycodes without knowing Sym is held, you'll type `[` when they meant `!`. You
**must** track the Sym modifier and have a Sym-specific keycode→character table.

There is no published table for this; you capture it from the device. A practical mapping captured on
current firmware (hold Sym, press the key):

| Symbol | keycode | Symbol | keycode |
|---|---|---|---|
| `?` | 93 | `)` | 94 |
| `!` | 26 | `-` | 80 |
| `@` | 27 | `/` | 71 |
| `#` | 39 | `:` | 92 |
| `$` | 40 | `'` | 81 |
| `%` | 41 | | |
| `&` | 51 | | |
| `*` | 52 | | |
| `(` | 53 | | |

Treat this as a starting point and verify on your own unit — firmware can shift these. To capture
them yourself, stop the launcher briefly (`systemctl --user stop APPLaunch.service`), read raw events
from the keyboard's `/dev/input/eventN`, and press Sym + each symbol; the codes with Sym held are
your table. Restart the launcher after.

### Key releases: remember the press-time mapping

One more subtlety: because the character a key produces depends on modifier state (Shift/Sym), you
must map a key **at press time** and emit that same mapping on **release** — don't re-map on release
using the *current* modifier state. Otherwise "press Shift+A, release Shift, release A" emits an `A`
down and an `a` up, leaving your hold-tracking inconsistent and keys "stuck." Remember each physical
key's press-time result and reuse it at release.

## A workable input recipe

Putting it together, an evdev → character/key layer that works:

1. Track `KEY_LEFTSHIFT`/`KEY_RIGHTSHIFT` → `shift_held`, and keycode **383** → `sym_held`. `continue`
   (don't emit) on the modifiers themselves.
2. Ignore auto-repeat events (value 2).
3. On a key **press**, compute the result in this order and store it keyed by the physical keycode:
   control keys first (Esc/Enter/arrows/Backspace/Delete/Tab) → if `sym_held`, the Sym table → else
   the normal printable map honoring `shift_held`.
4. On a key **release**, emit the stored mapping for that physical keycode and forget it.

This gives you arrows (via the Fn-translated keycodes), uppercase and shifted punctuation (Shift), and
the full symbol layer (Sym) — i.e. actual, usable text entry.

## A nicety: let the d-pad keys navigate without Fn

The bare `F / X / Z / C` keys type letters, but outside a text field there's nothing to type — so
many apps feel better if the bare `F/X/Z/C` keys act as the **d-pad** everywhere *except* while a
text field is focused, and require Fn for the arrows only inside text entry. (Both still work: the
Fn-translated `KEY_UP`/etc. keep functioning.) Switch on whether a text input is currently capturing.
It removes the need to reach for Fn just to move around a menu.

---

Next: the full build-and-ship pipeline — [building and packaging](06-building-and-packaging.md).
