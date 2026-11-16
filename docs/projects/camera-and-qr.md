# Camera capture and QR scanning

Inspect the camera stack on the target image. A CSI sensor's `/dev/video0` can be
a sensor/ISP node rather than a ready webcam stream. Mesh uses a fixed
libcamera/rpicam capture with bounded dimensions/time and in-memory decoding;
other apps may use a compatible official camera service. Check the actual backend,
permissions and runtime dependencies before choosing either path.

## Visible operation and ownership

Show Ready with an explicit keyboard action, publish Scanning/Busy before work
starts, ignore repeated starts and return an actionable result or retry. Correlate
results by request and target. Clear stale results before a new operation and
stop accepting late replies after dismissal. Explain whether Escape cancels work
or merely leaves the view; it does not automatically roll back a committed action.

Bound capture plus exposure/startup plus decode within a measured total deadline.
Give the owner a cancellation mechanism and control its helper/process group.
Camera-busy and missing-decoder failures are not equivalent to "no QR found".
Keep unrelated local saves and status updates responsive while capture is blocked.

## QR codes that change configuration

Decoded text is untrusted. Validate format, length, destination and permitted action.
For a secret/configuration import, separate capture, nonsecret preview and explicit
commit. Keep the secret at its owner; bind short-lived preview authorization to the
requesting session and exact reviewed configuration. Invalidate it on cancellation,
configuration change or teardown, including queued work. Announce actual commits
when their original view has gone away. These rules apply beyond radio channels.

## Acceptance checks

Test synthetic codes, malformed/oversized content, missing/busy camera, timeout,
repeated Return, cancellation and late/wrong-target replies. Qualify the actual
camera in good light and realistic distances on the supported image. Do not retain
private camera frames just for diagnostics or ship usable private QR codes in tests.
See the preserved [Mesh camera/import lessons](../case-studies/mesh.md#ui-and-asynchronous-operations).

[Project selector](README.md)
