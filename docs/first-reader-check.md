# Try the guide without our help

This is a usability check of the instructions, separate from testing an app.
Give a new builder the [short route](start-here.md) and
[counter walkthrough](first-app.md), without this project's chat history. Let
them choose a supported desktop environment. No device or private credentials
are needed for the first build.

## What to record

- Guide Git revision, operating system/architecture, compiler and CMake versions.
- Which route they followed and whether they found the correct dependency list.
- Whether they could build, locate the executable, open the counter, change the
  greeting and rebuild without unwritten assistance.
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

**Independent-builder check: pending.** Maintainer source/build/package checks
are recorded in the [walkthrough](first-app.md#verification-and-limits). They do
not establish that an unfamiliar builder can follow the guide unaided. No claim
of independent usability validation should be made until an actual reader has
completed and reported this exercise.

[Short route](start-here.md) · [Guide index](../README.md)
