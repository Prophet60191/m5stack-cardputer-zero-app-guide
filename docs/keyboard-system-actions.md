# Keyboard integration audit — 2026-11-27

## Scope and decision

This work covers Mesh, Wireless Surveyor, NFC Tools, App Shell and Tick & Bell only.
Quartermaster and other third-party applications are excluded and unchanged.
These apps use standalone Template-derived LVGL input. Keep that architecture;
do not decode events a second time in an app using the official shared runtime.

The device driver already resolves held, one-shot and locked Fn/Sym layers.
Our decoder translates its events, keeps per-device modifier/release ownership,
and checks all 32 symbols against an independent official fixture. Recognizing
an action code is not sufficient: these standalone apps lacked the system handler
which the official launcher/shared runtime supplies. That caused volume keys to
be consumed without changing volume. We reuse the official mixer implementation
unchanged, with a small app-owned adapter and normal-user OS interfaces.

## Official sources reviewed

- [Keyboard specifications](https://github.com/CardputerZero/cardputerzero.github.io/blob/main/docs/en/CP0_keys.md).
- [Official launcher](https://github.com/CardputerZero/launcher/tree/d59f15918c473bc61de13b4960d69ce0e7514899), specifically GlobalHintPolicy, setup_value_policy.hpp and cp0_audio_mixer_control / cp0_pulse_client. The four copied source files and their exact hashes are in ../contributions/template-system-keys/upstream.json.
- [Template](https://github.com/CardputerZero/Template/tree/477fa6d217b683e3084c361a757f03dc8ca9f753). Standalone integration adapts its input delivery; no firmware or OS keymap changes.

## Keyboard contract

| Keys | Behavior |
| --- | --- |
| Ordinary letters, Shift, all 32 Sym symbols | Text in an editor; existing app shortcuts outside typing |
| Tab / Shift+Tab | Forward / backward focus or the screen's documented tab action |
| Fn+Z/C/F/X | Left/right/up/down; typing uses cursor navigation |
| Fn+K/N; Fn+Backspace | Home/End; forward Delete |
| Fn+L/M | Page Up/Down in applicable lists; never text in an editor |
| Fn+H/J | Help / screenshot; preserve editor draft and cursor |
| Fn+A/S/D | Mute / volume down / up, 10% steps, 0–100% |
| Fn+U/I | Brightness down / up, 10% steps, 10–100% |
| Fn+Q/W/E | Play/pause / previous / next for one MPRIS player |
| Fn+1…0/O/P | F1–F12 semantic actions; unbound where no app feature exists |
| Fn+B | Insert semantic action; NFC's variable picker where applicable; otherwise unbound |
| Enter / Esc | Contextual accept/back; typing and overlays own their keys |

Mesh adds explicit Left/Z → Channels and Right/C → Direct Messages on its
unfiltered conversation list. Tab/Shift+Tab remain available. Search spans both
lists; composing and overlays keep their own keys.

System feedback is a short nonfocusable overlay. Bounded worker operations keep
LVGL responsive. Mute/media auto-repeats are ignored; level repeats are bounded
and released repeats are dropped. No player, several players or an unavailable
service produces a clear limitation message. This does not promise remote control
of a music app which does not expose MPRIS, or a general international IME.
No root audio process, new global key reader, input grab or new permissions.

## Verification boundaries

Decoder fixtures and synthetic evdev-to-editor tests cover mapping, release,
repeat, loss/disconnect, typing and shortcut ownership. Desktop and Debian arm64
suites are distinct from real hardware checks. SDL now maps Shift+Tab, paging,
function and media keys consistently with the native action contract.

A real normal-user Lockon probe successfully read and changed volume, mute and
brightness, then restored exact per-channel volume, mute and raw brightness.
That proves the OS backend, not that someone physically pressed every Fn key.
Installed-app evdev replay and physical acceptance must be recorded separately.
No NFC card writes, RF transmissions, scans, camera or GPS work is part of this
keyboard audit. Existing saved app data and settings must be preserved.

## Integration

See [the standalone adapter](../contributions/template-system-keys/README.md).
Keep it out of shared-runtime apps that already provide global system actions.

## Installed integration result

Mesh 0.1.23, Surveyor 0.2.2, NFC Tools 0.10.4, App Shell 0.1.1 and Tick & Bell 0.1.5 passed
normal-user installed-UI raw evdev volume/mute/brightness checks with actual
OS readback and visible feedback. Exact original mixer/backlight settings were
restored and existing saved files/database rows preserved. All three media
methods reached a synthetic MPRIS player; absent and ambiguous players were
reported without changing another app. Physical Fn/Sym presses are not claimed.
Tick & Bell's older standalone decoder/editor path also needed adaptation;
its dedicated editor and numeric-field tests preserve cursor/Help ownership.

All five also passed ordinary-user on-device 32-symbol/reader/editor fixture
replay. Tick & Bell retained its saved alarm state, configuration and scheduler
PID. Its desktop and arm64 suites each pass 5/5. These source changes reuse
official foundation work and do not modify device firmware or third-party apps.
