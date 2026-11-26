<a id="try-the-guide-without-our-help"></a>

# Try the guide on your own

This is a usability check of the instructions, separate from testing an app.
Give a new builder the [short route](start-here.md), without this project’s
chat history. Use the [App Shell](app-shell.md) to test the main first-app path;
use the [counter walkthrough](first-app.md) to test the smaller official-Template
exercise. Let the reader choose a supported desktop environment. No handheld
is needed for the first desktop build.

## What to record

- Guide Git revision, operating system/architecture, compiler and CMake versions.
- Which route they followed and whether they found the correct dependency list.
- For the App Shell: whether they could clone it, configure and open the
  simulator, change a screen, see the result, and build an arm64 package with
  their own app identity using only the README and guide.
- For the counter: whether they could build, locate the executable, change the
  greeting, and rebuild without unwritten assistance.
- Optionally, whether they could add the reset action from the walkthrough and
  confirm that the same key still changes the theme on the home screen. Record
  this separately from the first-build result.
- The first instruction that was unclear, its expected result and what happened.
- Whether they understood the difference between a desktop build, an arm64
  package, physical testing and a publishable app.
- Whether they could find the next recipe for their own idea without reading
  every peripheral chapter.

Do not collect private paths, network names, account details or complete logs
without reviewing/redacting them. A short error excerpt and tool versions are
usually enough. Do not install a template package over another developer's app.

## How to run the check

Ask the builder to explain what they expect before each milestone. Record help
provided, including any missing command supplied by the observer; a rescued step
is not an independent success. Time spent is useful context, not a performance
target. Stop on an unexpected privilege request, package collision or hardware
instruction unrelated to the chosen route.

Finish by asking: What could you skip? What did you read twice? What would you
build next, and which chapter would you open? Fix the instruction at its primary
home and retest the confusing step with a fresh reader when possible.

## Current status

**Independent-builder check: pending.** Maintainer build and packaging checks
are useful, but do not establish that an unfamiliar builder can follow the guide
unaided. No claim
of independent usability validation should be made until an actual reader has
completed and reported this exercise.

[Short route](start-here.md) · [Guide index](../README.md)
