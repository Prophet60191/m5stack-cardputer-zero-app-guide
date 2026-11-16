# Audio, recording and media playback

Start with the intended device image's ordinary user-session audio facilities or
a compatible official media service. Inspect the official [Music](https://github.com/CardputerZero/Music)
and [Recorder](https://github.com/CardputerZero/Recorder) apps as references, not
as proof that every backend, image or recording format has been tested here.
A privileged process may not inherit access to the user's audio session; avoid
privilege escalation as an audio-routing workaround.

## App behavior

Keep decoding/capture off the UI thread, bound buffers and define pause/stop/close
semantics. Own workers and device handles through cancellation and failure.
Make recording visible, require deliberate activation, choose a private destination
and explain retention/deletion. Permission failure, busy device, unsupported codec
and storage-full errors should produce different actionable messages.

Budget waveform/album-art assets and redraw work for the small display/memory.
Define which controls need physical press/release/repeat semantics instead of text
or generic navigation. Keep playback/recording state confirmed by its owner.

## Acceptance checks

Test synthetic media, malformed/truncated content, no output/input device, concurrent
ownership, cancellation, full storage and restart. Qualify speaker/microphone,
latency, clipping, route changes and long-running resource use on the intended
image. Those are proposed acceptance checks, not results established by Mesh.

[Project selector](README.md)
