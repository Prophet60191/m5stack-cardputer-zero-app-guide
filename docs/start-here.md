# Build your first app

You do not need to read the entire guide before building. Start with a small
working screen, then add the facilities your idea actually needs. This route is
for **CardputerZero running Debian**, not the ESP32 Cardputer or Cardputer ADV.

## Choose a starting point

- **Build your own app:** Use the [App Shell](app-shell.md) for a menu, lists,
  a small form, and a detail page you can adapt.
- **See a completed example:** [Tick & Bell](case-studies/tick-bell.md) shows
  how the patterns serve a real timer and alarm.
- **Try one small exercise:** Use the counter route below to learn the build
  and input basics without adopting the shell.

## The short route

1. **Define one useful task.** Write down what the user can do, what data survives
   closing, and whether any hardware or network access is required. A local
   counter needs neither a supervisor nor a setup wizard.
2. **Build the official starting point.** Follow the
   [counter walkthrough](first-app.md). It takes you from pinned source to a
   desktop build and an inspectable arm64 package. No device is needed yet.
3. **Make it yours.** Change the greeting, then try the counter reset exercise.
   Rebuild and check both changes in the simulator. Follow a key press through
   the viewmodel to the screen before replacing any of the Template's structure.
4. **Choose only relevant extras.** Use the table below. Read the linked recipe
   when adding that capability; the recipe is not a requirement for every app.
5. **Try it on a handheld (optional).** The [first-device walkthrough](first-device-app.md) gives a separate saved counter its own package identity, then checks physical controls, upgrade and rollback.
6. **Prepare a real app for release.** Give it its own identity, handle errors,
   preserve attribution, and follow [build/install checks](06-building-and-packaging.md)
   and [security/publishing](08-security-and-publishing.md). A successful build
   is a starting point, not a release certificate.

Stop after the greeting if you only want a first working example, or do the reset
exercise to add a feature of your own. The fuller reference
is there when the next design question arises.

## Which sections do I need next?

| Your next need | Read next |
|---|---|
| Another local screen, a timer, calculator or game | [Local utilities](projects/local-utilities.md); [UI](04-ui-and-polish.md) |
| Notes, saved records, drafts or conversations | [Persistence/messaging](projects/messaging.md); [identity and durable intent](03-architecture.md#preserve-identity-and-durable-intent-safely) |
| Keyboard text entry | [Keyboard](05-keyboard.md); evaluate the official input path before adding a decoder |
| A website, network service or remote-control connection | [Networking](projects/networking.md); [security](08-security-and-publishing.md) |
| GPS, camera, NFC, LoRa or another peripheral | [Project selector](projects/README.md); use the specific peripheral recipe |
| Playback or recording | [Audio/media](projects/audio-and-media.md) |
| Slow work or more than one resource owner | [Architecture choices](03-architecture.md); a separate service is one option |
| An installed app with an icon that won’t open | [Check for a missing device library](device-app-troubleshooting.md#if-the-executable-is-there-check-what-linux-can-load) |
| A Debian installer, upgrade or Store listing | [Packaging](06-building-and-packaging.md); [worked upgrade and rollback](upgrade-existing-app.md); [Store readiness](store-readiness.md) |

## Understand the labels

**Platform requirements** describe the device, launcher and packaging contract.
**Project recipes** apply only to the facilities you use. **Personal UI preferences**
record my chosen appearance and interaction; they are not official requirements.
**Case studies** record what a particular project taught me, with its own test limits.

Start by inspecting official guidance and code. Reuse what fits; adapt what your
app needs. Record the reason for a departure before treating it as a reusable
improvement. [The component comparison](components.md) and
[library principles](library-principles.md) explain this distinction.

## Follow the source as you build

| Label | What it means |
|---|---|
| Official | M5Stack/CardputerZero source or instructions. Where a build is reproduced, follow the linked revision rather than assuming the latest code is the same. |
| Adapted | A named upstream or project pattern reused with changes. The guide names the source and the difference. |
| Guide contribution | A walkthrough, patch, test, component, or verification result maintained with this guide, not an official release or endorsement. |

The walkthroughs label these handoffs at the steps where they happen. Keep the
original notices with code and assets you reuse. A physical check in one app
does not certify another app, device or image.

## Keep an honest progress record

Use separate milestones: source builds; desktop behavior checked; arm64 package
built and inspected; installed app checked; physical input/peripherals checked;
release reviewed. Mark unperformed checks **pending**, with the reason. A stationary
GPS or Wi-Fi check, for example, cannot prove performance while walking a survey.

The [independent-reader check](first-reader-check.md) is a short handoff for
someone trying this guide without the original chat history. Their experience will tell
me which instructions still need work.

[Counter walkthrough](first-app.md) · [Full reference](../README.md#common-foundation)
