# NFC, Caps and other hardware projects

Use the documented interface for the exact board/peripheral revision. Determine
whether an official compatible service already owns the resource. Record power,
mux, GPIO/I2C/SPI/UART, permissions, shared-pin/rail conflicts and teardown before
implementing acquisition. The [LoRa sequence](../07-radio-bring-up.md) is specific
to that Cap; it is not an NFC, audio or generic-GPIO recipe.

## Resource ownership and failure

Choose one owner and serialize conflicting operations. Acquire only necessary
permissions and restore resources according to their safe order and prior state.
Distinguish absent, busy, unsupported and failed initialization. Provide an
appropriate retry/close path where useful, but do not claim that a presence dialog
can verify an antenna or that every peripheral supports safe hot swapping.

If a process changes persistent power/mux state or starts child processes,
[design abrupt-death recovery](../03-architecture.md#why-a-separate-supervisor).
Stop/reap children before restoring shared hardware. Do not kill unrelated owners
or reset system configuration to make a probe succeed. Test ordinary close,
initialization failure and interruption with fake resources before device work.

## Acceptance checks

Check missing/busy hardware behavior and shared-resource transitions using the
manufacturer's safe procedure. Verify permissions as the normal application user.
Confirm actual hardware release after exit/failure and that another app can use
it afterward. Disconnect/reconnect tests are appropriate only when the hardware
supports them safely. Document qualification per board/image/peripheral, including
power-cycle requirements; a UI simulator cannot qualify electrical behavior.

This section is development guidance for relevant projects. It does not add a Cap
presence feature or change the current Mesh application's radio behavior.

[Project selector](README.md)
