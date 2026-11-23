# Choose the project sections you need

First app? Take the [short route](../start-here.md) before choosing extras.

All apps use the [common foundation](../../README.md#common-foundation). Add the
sections below only when their capabilities apply. A topic being documented does
not mean it is implemented or qualified in every example application.

| Project type | Additional guidance | Evidence status |
|---|---|---|
| Calculator, notes, timer, simple game | [Local utilities](local-utilities.md) | Architecture/acceptance recipe; no new device app claimed |
| Text, drafts, searchable records, messaging | [Persistence and messaging](messaging.md) | General rules with detailed Mesh examples; transports differ |
| GPS receiver or maps | [GPS and maps](gps-and-maps.md) | Parser/freshness patterns; outdoor fix and other hardware require qualification |
| Camera or QR scanner | [Camera and QR](camera-and-qr.md) | Mesh CSI capture experience; qualify the actual sensor/image/decoder |
| NFC, GPIO/I2C/SPI or another Cap | [Hardware ownership](hardware.md) | Conditional safety/lifecycle recipe; verify each peripheral's documentation |
| LoRa Cap | [Radio bring-up](../07-radio-bring-up.md) plus [hardware ownership](hardware.md) | Board/Cap-specific wiring and lessons; not a universal pinout |
| Network client/server or remote control | [Networking](networking.md) | Threat-model/acceptance recipe; private local daemons and remote services differ |
| Audio, recording or media playback | [Audio and media](audio-and-media.md) | Integration recipe and official examples; not qualified by Mesh tests |

For any new hardware capability, first identify the board/image/peripheral,
permissions, safe acquisition/release sequence and unsupported behavior. Use a
fake implementation for UI tests. Add real-device acceptance checks separately.
Do not copy a Mesh-only channel, key or daemon dependency into an unrelated app.

[Guide index](../../README.md) · [Preserved lessons](../lesson-index.md)
