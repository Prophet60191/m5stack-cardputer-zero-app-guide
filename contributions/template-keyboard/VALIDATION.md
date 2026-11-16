# Keyboard proposal validation

Exact source and patch provenance: [upstream.json](upstream.json).

## Validation matrix

| Environment/path | Check | Evidence |
|---|---|---|
| macOS arm64, desktop | Full Template and optional example compile; decoder tests under ASAN/UBSAN | Passed locally from a clean checkout through the final-patch verifier |
| Debian 13 arm64, native framebuffer build | Full Template/example compile; portable and actual-reader/editor CTests under ASAN/UBSAN | Passed locally from a clean checkout in an ordinary-user isolated container, synthetic pipes only (including current owner-scoped cleanup) |
| Clean pinned upstream source | Reviewed patch applies without hand-editing the baseline | Passed in both clean-checkout verifications; CI repeats this check |
| Default example-disabled build | Normal Template UI remains buildable | Passed after each example-enabled build; separate default-app compilation |
| Ubuntu x86_64 desktop | Full build and Linux actual-reader/editor sanitizer tests | Automated by the pinned-source workflow; inspect the result for the exact guide commit |

The [CI workflow](../../.github/workflows/keyboard-proposal.yml) repeats clean-source
patch/build/test/default-build verification on Ubuntu x86_64 and native Debian 13
arm64. [Current results](https://github.com/Prophet60191/m5stack-cardputer-zero-app-guide/actions/workflows/keyboard-proposal.yml)
must be matched to the reviewed guide commit; an earlier green run does not qualify
later patch changes. Guide links, the existing preflight and proposal-verifier
guards also pass 22 local Python tests. Store preflight behavior/policy pins are unchanged.

## Remaining qualification

The complete physical key sweep, driver/firmware hold/one-shot/lock transitions,
supported image variants, USB international layouts and manual default-demo/Help/
navigation behavior have not been newly qualified on a Cardputer by this guide pass.
The source Mesh revision has its own narrower prior evidence; do not transfer its
device qualification to this Template build. No device package was installed.

The proposal is not an accepted upstream change. Compatibility of the shared
SCons/cp0 backend with the CMake Template has not been established by this patch;
applications should choose one decoding path.
