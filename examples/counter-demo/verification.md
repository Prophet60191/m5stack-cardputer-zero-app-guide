# Guide Counter verification

Checked November 26, 2026 against Template `477fa6d217b683e3084c361a757f03dc8ca9f753`
and LVGL `85aa60d18b3d5e5588d7b247abf90198f07c8a63`. A clean pinned Template
checkout accepted the patch. A fresh dependency install was not tested.

| Check | Result |
| --- | --- |
| macOS arm64 builds and normal SDL event handling with synthetic key events | Both versions built. Version 0.1.0 saved 3 and exited; 0.2.0 reopened at 3, saved 4 and exited; 0.1.0 reopened at 4. About showed the correct versions. |
| Save failure and model tests | A blocked write kept the last displayed count and showed an error. Malformed state, count bounds, rejected writes and temporary-file cleanup tested with disposable files. |
| Debian 13 arm64 packages | Both built and inspected in a network-disabled container with provisioned dependencies. ARM64 executables, matching launcher/binary/icon, no service, no maintainer scripts. |
| Debian package lifecycle | Installed 0.1.0, upgraded to 0.2.0, downgraded to 0.1.0 and removed it in a disposable arm64 container. A separate home-state fixture survived; the launcher entry was removed. The container did not launch the handheld UI. |
| Handheld and independent-reader testing | Pending. The test above does not certify the real display, launcher or physical keys. No Store submission. |

These SHA-256 values identify the exact artifacts tested, not expected hashes
for every rebuild. Build timestamps can change the package bytes.

```text
0.1.0-rev1  0a913ae0873a6f4fa2f32d6a0dddd1bf7b6af32d5ff2843ee204c68a82c6f4f5
0.2.0-rev1  1c2b3a016dd9a2dc66083b99567d7c552de60d8f4d82283d56a9c277d631d81f
```

[Device walkthrough](../../docs/first-device-app.md)
